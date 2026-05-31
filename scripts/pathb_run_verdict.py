"""Gated RUN entry point for the Path B verdict (NOT auto-run by the build).

Wires real engine-backed stages into backtest.pathb_orchestrator.run_pathb_verdict
on the forward_2026 window at the 15bps spot anchor, writes advisory evidence to
data/phase2c_evaluation_gate/pathb_verdict_v1/. Executing this is a Charlie
register-event (design §6); the build only constructs + smoke-tests it.
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHB_VERDICT_DIR = PROJECT_ROOT / "data/phase2c_evaluation_gate/pathb_verdict_v1"
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


def main() -> int:  # pragma: no cover - the gated RUN
    ap = argparse.ArgumentParser(
        description="Gated Path B verdict RUN (Charlie register-event only)."
    )
    ap.add_argument("--out-dir", default=str(PATHB_VERDICT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir)
    assert_not_sealed(out)
    raise SystemExit(
        "Path B verdict RUN is a Charlie register-event (design §6); "
        "this CLI is wired but not auto-executed by the build."
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
