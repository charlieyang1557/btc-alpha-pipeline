"""Manual trade verification helper.

Human-facing inspection tool that cross-references trade log CSVs
against raw OHLCV data to verify execution correctness.

For each audited trade, verifies:
- Signal bar timestamp and conditions
- Fill bar: exactly 1 bar after signal
- Fill price matches fill bar's open price
- Commission equals 7bps of trade value
- Fill bar has volume > 0
- Context bars around the fill

Usage:
    python -m backtest.trade_audit --run-id <UUID> --trade-index 0 1 2
    python -m backtest.trade_audit --run-id <UUID> --all
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "data" / "results"
DEFAULT_PARQUET = PROJECT_ROOT / "data" / "raw" / "btcusdt_1h.parquet"

EXPECTED_COMMISSION_RATE = 0.0007  # 7bps per side
PRICE_TOLERANCE = 1e-6
COMMISSION_TOLERANCE = 1e-4


def load_trade_csv(run_id: str) -> pd.DataFrame:
    """Load trade log CSV for a given run.

    Args:
        run_id: UUID of the run.

    Returns:
        DataFrame with trade records.

    Raises:
        FileNotFoundError: If the trade CSV does not exist.
    """
    csv_path = RESULTS_DIR / f"trades_{run_id}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Trade CSV not found: {csv_path}")
    return pd.read_csv(csv_path)


def load_ohlcv(parquet_path: Path = DEFAULT_PARQUET) -> pd.DataFrame:
    """Load raw OHLCV data indexed by open_time_utc.

    Args:
        parquet_path: Path to the canonical parquet file.

    Returns:
        DataFrame indexed by tz-naive open_time_utc.

    Raises:
        FileNotFoundError: If the parquet file does not exist.
    """
    if not parquet_path.exists():
        raise FileNotFoundError(f"Parquet not found: {parquet_path}")

    df = pd.read_parquet(parquet_path)
    df = df.set_index("open_time_utc").sort_index()
    df.index = df.index.tz_localize(None)
    return df


def audit_trade(
    trade: pd.Series,
    ohlcv: pd.DataFrame,
    context_bars: int = 5,
) -> dict:
    """Audit a single trade against raw OHLCV data.

    Performs these verifications:
    1. Entry fill price == fill bar's open price
    2. Exit fill price == fill bar's open price
    3. Entry commission == 7bps * (size * entry_price)
    4. Exit commission == 7bps * (size * exit_price)
    5. Fill bars have volume > 0
    6. Fill bar is exactly 1 bar after signal bar

    Args:
        trade: Series with trade record fields.
        ohlcv: OHLCV DataFrame indexed by datetime.
        context_bars: Number of bars to show before/after fills.

    Returns:
        Dict with audit results and context data.
    """
    result = {"trade_id": int(trade["trade_id"]), "checks": {}, "context": {}}

    # Parse timestamps — strip timezone to match tz-naive OHLCV index
    entry_signal_dt = pd.Timestamp(trade["entry_signal_time_utc"]).tz_localize(None)
    entry_fill_dt = pd.Timestamp(trade["entry_time_utc"]).tz_localize(None)
    exit_signal_dt = pd.Timestamp(trade["exit_signal_time_utc"]).tz_localize(None)
    exit_fill_dt = pd.Timestamp(trade["exit_time_utc"]).tz_localize(None)

    size = trade["size"]

    # --- Entry checks ---

    # Check entry fill price matches fill bar's open
    entry_price_match = False
    if entry_fill_dt in ohlcv.index:
        expected_entry_price = ohlcv.loc[entry_fill_dt, "open"]
        entry_price_match = abs(trade["entry_price"] - expected_entry_price) < PRICE_TOLERANCE
        result["checks"]["entry_price_match"] = {
            "pass": entry_price_match,
            "expected": float(expected_entry_price),
            "actual": float(trade["entry_price"]),
        }
    else:
        result["checks"]["entry_price_match"] = {
            "pass": False,
            "error": f"Fill bar {entry_fill_dt} not found in OHLCV data",
        }

    # Check entry commission
    expected_entry_comm = size * trade["entry_price"] * EXPECTED_COMMISSION_RATE
    entry_comm_match = abs(trade["entry_commission"] - expected_entry_comm) < COMMISSION_TOLERANCE
    result["checks"]["entry_commission"] = {
        "pass": entry_comm_match,
        "expected": round(expected_entry_comm, 6),
        "actual": float(trade["entry_commission"]),
    }

    # Check entry fill bar has volume > 0
    if entry_fill_dt in ohlcv.index:
        entry_vol = float(ohlcv.loc[entry_fill_dt, "volume"])
        result["checks"]["entry_volume_nonzero"] = {
            "pass": entry_vol > 0,
            "volume": entry_vol,
        }

    # Check entry fill is 1 bar after signal
    if entry_signal_dt in ohlcv.index and entry_fill_dt in ohlcv.index:
        signal_idx = ohlcv.index.get_loc(entry_signal_dt)
        fill_idx = ohlcv.index.get_loc(entry_fill_dt)
        bars_apart = fill_idx - signal_idx
        result["checks"]["entry_next_bar"] = {
            "pass": bars_apart == 1,
            "signal_bar_index": int(signal_idx),
            "fill_bar_index": int(fill_idx),
            "bars_apart": int(bars_apart),
        }

    # --- Exit checks ---

    if exit_fill_dt in ohlcv.index:
        expected_exit_price = ohlcv.loc[exit_fill_dt, "open"]
        exit_price_match = abs(trade["exit_price"] - expected_exit_price) < PRICE_TOLERANCE
        result["checks"]["exit_price_match"] = {
            "pass": exit_price_match,
            "expected": float(expected_exit_price),
            "actual": float(trade["exit_price"]),
        }
    else:
        result["checks"]["exit_price_match"] = {
            "pass": False,
            "error": f"Fill bar {exit_fill_dt} not found in OHLCV data",
        }

    expected_exit_comm = size * trade["exit_price"] * EXPECTED_COMMISSION_RATE
    exit_comm_match = abs(trade["exit_commission"] - expected_exit_comm) < COMMISSION_TOLERANCE
    result["checks"]["exit_commission"] = {
        "pass": exit_comm_match,
        "expected": round(expected_exit_comm, 6),
        "actual": float(trade["exit_commission"]),
    }

    if exit_fill_dt in ohlcv.index:
        exit_vol = float(ohlcv.loc[exit_fill_dt, "volume"])
        result["checks"]["exit_volume_nonzero"] = {
            "pass": exit_vol > 0,
            "volume": exit_vol,
        }

    if exit_signal_dt in ohlcv.index and exit_fill_dt in ohlcv.index:
        signal_idx = ohlcv.index.get_loc(exit_signal_dt)
        fill_idx = ohlcv.index.get_loc(exit_fill_dt)
        bars_apart = fill_idx - signal_idx
        result["checks"]["exit_next_bar"] = {
            "pass": bars_apart == 1,
            "signal_bar_index": int(signal_idx),
            "fill_bar_index": int(fill_idx),
            "bars_apart": int(bars_apart),
        }

    # --- Context bars ---

    for label, dt in [("entry", entry_fill_dt), ("exit", exit_fill_dt)]:
        if dt in ohlcv.index:
            idx = ohlcv.index.get_loc(dt)
            start = max(0, idx - context_bars)
            end = min(len(ohlcv), idx + context_bars + 1)
            ctx = ohlcv.iloc[start:end][["open", "high", "low", "close", "volume"]].copy()
            ctx.index = ctx.index.astype(str)
            result["context"][f"{label}_bars"] = ctx.to_dict(orient="index")

    return result


def print_audit(audit_result: dict) -> None:
    """Pretty-print a single trade audit result.

    Args:
        audit_result: Dict from audit_trade().
    """
    tid = audit_result["trade_id"]
    checks = audit_result["checks"]

    print(f"\n{'='*70}")
    print(f"  TRADE AUDIT — Trade #{tid}")
    print(f"{'='*70}")

    all_pass = True
    for check_name, check_data in checks.items():
        passed = check_data.get("pass", False)
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False

        print(f"\n  [{status}] {check_name}")
        for k, v in check_data.items():
            if k != "pass":
                print(f"         {k}: {v}")

    # Print context bars
    for label in ["entry_bars", "exit_bars"]:
        if label in audit_result.get("context", {}):
            print(f"\n  Context — {label}:")
            ctx = audit_result["context"][label]
            print(f"  {'Timestamp':<22s} {'Open':>10s} {'High':>10s} {'Low':>10s} {'Close':>10s} {'Volume':>12s}")
            print(f"  {'-'*22} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*12}")
            for ts, bar in ctx.items():
                print(
                    f"  {ts:<22s} {bar['open']:>10.2f} {bar['high']:>10.2f} "
                    f"{bar['low']:>10.2f} {bar['close']:>10.2f} {bar['volume']:>12.1f}"
                )

    print(f"\n  {'='*70}")
    verdict = "ALL CHECKS PASSED" if all_pass else "SOME CHECKS FAILED"
    print(f"  VERDICT: {verdict}")
    print(f"  {'='*70}\n")


def main() -> int:
    """CLI entry point for trade auditing.

    Returns:
        Exit code: 0 if all checks pass, 1 if any fail.
    """
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(description="Manual trade audit helper")
    parser.add_argument(
        "--run-id",
        type=str,
        required=True,
        help="Run UUID to audit",
    )
    parser.add_argument(
        "--trade-index",
        type=int,
        nargs="*",
        default=None,
        help="Trade indices to audit (0-based). Omit for --all.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Audit all trades",
    )
    parser.add_argument(
        "--parquet",
        type=str,
        default=str(DEFAULT_PARQUET),
        help="Path to OHLCV parquet file",
    )
    parser.add_argument(
        "--context-bars",
        type=int,
        default=5,
        help="Context bars before/after fill (default: 5)",
    )
    args = parser.parse_args()

    # Load data
    trades_df = load_trade_csv(args.run_id)
    ohlcv = load_ohlcv(Path(args.parquet))

    # Select trades to audit
    if args.all:
        indices = list(range(len(trades_df)))
    elif args.trade_index:
        indices = args.trade_index
    else:
        # Default: first, middle, last
        n = len(trades_df)
        indices = sorted(set([0, n // 2, n - 1]))

    all_pass = True
    for idx in indices:
        if idx < 0 or idx >= len(trades_df):
            logger.warning("Trade index %d out of range (0-%d)", idx, len(trades_df) - 1)
            continue

        trade = trades_df.iloc[idx]
        audit_result = audit_trade(trade, ohlcv, context_bars=args.context_bars)
        print_audit(audit_result)

        for check in audit_result["checks"].values():
            if not check.get("pass", False):
                all_pass = False

    if all_pass:
        print("ALL AUDITED TRADES PASSED")
    else:
        print("SOME TRADES HAVE FAILING CHECKS — INVESTIGATE BEFORE PROCEEDING")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
