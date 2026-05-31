# scripts/pathb_step0_diagnostic.py
"""Path B Step 0: read-only re-score of the locked cohort under the Path B N*.

Read-only by construction. It consumes the sealed cohort dir
(``phase4_forward_2026_15bps_v1``) WITHOUT writing to it, runs the
forward-holdout single-run lineage guard
(``check_evaluation_semantics_or_raise`` — NOT the walk-forward guard) and
the 15bps cost-anchor preflight (``_assert_cost_anchor_15bps_spot``) on the
aggregate ``holdout_summary.json`` before any consumption, and writes its
diagnostic re-score into a SEPARATE Path B namespace dir
(``pathb_step0_diagnostic_v1``), never the cohort dir.

N* is Step -1 human-locked (PATHB_N_STAR); referenced symbolically here.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import os

from backtest.tier6_dsr import (
    DEFAULT_OUT_DIR as SEALED_TIER6_DIR,
    HOLDOUT_DIR,
    PROJECT_ROOT,
    _assert_cost_anchor_15bps_spot,
    _evaluate_one,
    _read_cohort_csv,
)
from backtest.wf_lineage import (
    check_evaluation_semantics_or_raise,
    check_wf_semantics_or_raise,  # imported so a regression that swaps guards is visible
)

logger = logging.getLogger("pathb_step0")

# Step -1 LOCK: N* = 3 (minimal grid — 3 hypotheses × 1 variant each, no sweep).
PATHB_N_STAR = 3

# Path B namespace — physically isolated from the sealed cohort dir.
DEFAULT_PATHB_STEP0_DIR = (
    PROJECT_ROOT / "data/phase2c_evaluation_gate/pathb_step0_diagnostic_v1"
)


def run_step0(
    cohort_dir: Path = HOLDOUT_DIR,
    out_dir: Path = DEFAULT_PATHB_STEP0_DIR,
    n_star: int = PATHB_N_STAR,
    write: bool = True,
) -> dict:
    """Re-score the cohort read-only; emit a diagnostic into the Path B namespace.

    Args:
        cohort_dir: Sealed cohort directory (READ ONLY; never written).
        out_dir: Path B namespace output dir (default DEFAULT_PATHB_STEP0_DIR).
        n_star: Step -1 locked multiplicity (default PATHB_N_STAR).
        write: When True, write the diagnostic CSV/JSON into out_dir.

    Returns:
        A dict with ``rows``, ``n_star``, ``read_only=True`` and
        ``promotion_side_effect=False`` (this script NEVER promotes).

    Raises:
        ValueError: On a forward-holdout single-run lineage-guard failure or a
            non-15bps-spot cost anchor (both fire before any cohort read).
    """
    summary_path = cohort_dir / "holdout_summary.json"
    summary_dict = json.loads(summary_path.read_text())
    # Forward holdout is a SINGLE-RUN evaluation -> evaluation-semantics guard
    # (single_run_holdout_v1), NOT the walk-forward guard. Fires before consume.
    check_evaluation_semantics_or_raise(summary_dict, artifact_path=str(summary_path))
    _assert_cost_anchor_15bps_spot(summary_dict)

    df = _read_cohort_csv(holdout_dir=cohort_dir)
    rows = [
        _evaluate_one(h, df, n_star=n_star, holdout_dir=cohort_dir)
        for h in df["hypothesis_hash"].tolist()
    ]

    if write:
        for _sealed in (cohort_dir, SEALED_TIER6_DIR):
            try:
                _same = os.path.samefile(out_dir, _sealed)
            except OSError:
                _same = Path(out_dir).resolve() == Path(_sealed).resolve()
            if _same:
                raise ValueError(
                    f"REFUSING: out_dir {out_dir} resolves to a sealed/read-only "
                    f"dir ({_sealed}); the Step-0 diagnostic must write to a "
                    f"NON-sealed Path B namespace."
                )
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "pathb_step0_rescore.json").write_text(
            json.dumps(
                {
                    "n_star": n_star,
                    "cohort_dir": str(cohort_dir),
                    "read_only": True,
                    "rows": rows,
                },
                indent=2,
                default=str,
            )
        )

    return {
        "rows": rows,
        "n_star": n_star,
        "read_only": True,
        "promotion_side_effect": False,
    }


def _configure_logging() -> None:
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        "%(asctime)s.%(msecs)03dZ %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    fmt.converter = time.gmtime
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.pathb_step0_diagnostic")
    parser.add_argument("--cohort-dir", default=str(HOLDOUT_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_PATHB_STEP0_DIR))
    parser.add_argument("--n-star", type=int, default=PATHB_N_STAR)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    _configure_logging()
    try:
        res = run_step0(
            cohort_dir=Path(args.cohort_dir),
            out_dir=Path(args.out_dir),
            n_star=args.n_star,
            write=not args.dry_run,
        )
    except (ValueError, OSError) as exc:
        logger.error("pathb_step0 FAILED: %s", exc)
        return 1
    logger.info(
        "pathb_step0 done: rows=%d n_star=%d read_only=%s",
        len(res["rows"]), res["n_star"], res["read_only"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
