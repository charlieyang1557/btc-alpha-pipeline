# scripts/pathb_cost_equivalence.py
"""Assert the cohort's net-return config equals the Tier-5 15bps spot anchor.

CLAUDE.md Conservative-Anchor Gate: the cohort was scored under
config/execution_phase4_15bps.yaml; the Tier-5 anchor is
config/execution_phaseb_spot_15bps.yaml. The two are documented as
functionally identical bodies (differ only by header + cost_model.name + SHA).
This guard parses both cost_model blocks and asserts identical fee + slippage,
reusing tier6_dsr's per-side cost helper so the bps arithmetic is single-source.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from backtest.tier6_dsr import PROJECT_ROOT, _per_side_cost_bps

PHASE4_CFG = PROJECT_ROOT / "config/execution_phase4_15bps.yaml"
ANCHOR_CFG = PROJECT_ROOT / "config/execution_phaseb_spot_15bps.yaml"


def _load_cost_model(path: Path) -> dict:
    """Parse and return the ``cost_model`` block of an execution YAML.

    Args:
        path: Execution config path.

    Returns:
        The ``cost_model`` dict.

    Raises:
        ValueError: If the file lacks a ``cost_model`` block.
    """
    cfg = yaml.safe_load(path.read_text()) or {}
    cm = cfg.get("cost_model")
    if not isinstance(cm, dict):
        raise ValueError(f"cost-equivalence: {path} has no cost_model block")
    return cm


def assert_cost_equivalence() -> dict:
    """Assert Phase4 cohort config fee/slippage equals the Tier-5 spot anchor.

    Returns:
        A dict echoing both configs' fee/slippage, the shared per-side bps, and
        ``equivalent=True`` on success.

    Raises:
        ValueError: If fee or slippage differ between the two configs.
    """
    phase4 = _load_cost_model(PHASE4_CFG)
    anchor = _load_cost_model(ANCHOR_CFG)

    fee = float(phase4.get("default_fee_bps", 0.0))
    slip = float(phase4.get("slippage_bps", 0.0))
    a_fee = float(anchor.get("default_fee_bps", 0.0))
    a_slip = float(anchor.get("slippage_bps", 0.0))

    if fee != a_fee or slip != a_slip:
        raise ValueError(
            f"cost-equivalence FAILED: phase4 fee/slip=({fee},{slip}) != "
            f"anchor fee/slip=({a_fee},{a_slip}); the cohort net-return config "
            f"must equal the Tier-5 15bps spot anchor."
        )
    return {
        "fee_bps": fee,
        "slippage_bps": slip,
        "anchor_fee_bps": a_fee,
        "anchor_slippage_bps": a_slip,
        "per_side_bps": _per_side_cost_bps(phase4),
        "equivalent": True,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI: print the cost-equivalence result as JSON; exit 1 on mismatch."""
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        prog="python -m scripts.pathb_cost_equivalence",
        description="Assert the Path B cohort net-return config equals the "
        "Tier-5 15bps spot anchor (fee + slippage).",
    )
    parser.parse_args(argv)
    try:
        result = assert_cost_equivalence()
    except ValueError as exc:
        print(f"cost-equivalence FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
