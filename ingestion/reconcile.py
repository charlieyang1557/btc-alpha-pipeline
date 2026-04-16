"""
Reconcile existing and new OHLCV data into the canonical parquet file.

Steps:
1. Archive the current canonical file.
2. Load existing + new DataFrames.
3. Concatenate, sort, deduplicate (prefer binance_vision on conflict).
4. Remove any partial candle at the end.
5. Verify no gaps in the final dataset.
6. Save as the new canonical file.
7. Log reconciliation stats.

Usage:
    python -m ingestion.reconcile --existing data/raw/btcusdt_1h.parquet --new data/raw/btcusdt_1h_update.parquet
    python -m ingestion.reconcile --existing data/raw/btcusdt_1h.parquet --new data/raw/btcusdt_1h_update.parquet --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.validators import save_report, validate_ohlcv

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = PROJECT_ROOT / "data" / "raw" / "archive"
QUALITY_DIR = PROJECT_ROOT / "data" / "quality"

# Source priority for deduplication. Lower number = preferred.
# "binance_vision" is the bulk historical archive (ground truth).
# "ccxt_binance" is the live Binance global API.
# Other venues (ccxt_binanceus, etc.) should NOT be mixed into
# a Binance global canonical file — check_venue_compatibility() enforces this.
SOURCE_PRIORITY = {"binance_vision": 0, "ccxt_binance": 1}

# Venues that are compatible with each other for merging.
# binance_vision and ccxt_binance both come from Binance global.
# binanceus is a separate venue and must NOT be mixed in.
COMPATIBLE_VENUES = {"binance_vision", "ccxt_binance"}


def archive_file(file_path: Path) -> Path | None:
    """Archive the current canonical parquet file before overwriting.

    Creates a timestamped copy in data/raw/archive/.

    Args:
        file_path: Path to the canonical parquet file.

    Returns:
        Path to the archived file, or None if source doesn't exist.
    """
    if not file_path.exists():
        logger.warning("No file to archive: %s", file_path)
        return None

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    archive_path = ARCHIVE_DIR / archive_name

    # Copy file (not move — we still need the original until merge succeeds)
    import shutil
    shutil.copy2(file_path, archive_path)
    logger.info("Archived %s → %s", file_path.name, archive_path)
    return archive_path


def check_venue_compatibility(
    existing_df: pd.DataFrame,
    new_df: pd.DataFrame,
) -> dict[str, Any]:
    """Check that existing and new data come from compatible venues.

    Binance global (binance_vision, ccxt_binance) and Binance.US
    (ccxt_binanceus) are separate markets with different liquidity
    and order flow. Merging them produces an incoherent dataset.

    Args:
        existing_df: Current canonical DataFrame.
        new_df: New rows to merge in.

    Returns:
        dict with 'compatible' (bool), 'existing_sources' (set),
        'new_sources' (set), and 'reason' (str or None).
    """
    existing_sources = set(existing_df["source"].dropna().unique())
    new_sources = set(new_df["source"].dropna().unique())
    all_sources = existing_sources | new_sources

    incompatible = all_sources - COMPATIBLE_VENUES
    if incompatible:
        return {
            "compatible": False,
            "existing_sources": existing_sources,
            "new_sources": new_sources,
            "reason": (
                f"Incompatible venue(s) detected: {sorted(incompatible)}. "
                f"Only {sorted(COMPATIBLE_VENUES)} can be merged into the "
                f"same canonical file. Binance.US is a separate market — "
                f"use a separate dataset path for it."
            ),
        }

    return {
        "compatible": True,
        "existing_sources": existing_sources,
        "new_sources": new_sources,
        "reason": None,
    }


def verify_overlap(
    existing_df: pd.DataFrame,
    new_df: pd.DataFrame,
    threshold: float = 0.0001,
) -> dict[str, Any]:
    """Verify that overlapping rows between existing and new data agree on OHLC prices.

    Per PHASE0_BLUEPRINT: prices must match within 0.01% in the overlap period.

    Args:
        existing_df: Current canonical DataFrame.
        new_df: New rows to merge in.
        threshold: Maximum allowed relative deviation (default 0.0001 = 0.01%).

    Returns:
        dict with 'passed' (bool), 'overlap_rows' (int), and 'details' (list of deviations).
    """
    overlap = pd.merge(
        existing_df[["open_time_utc", "open", "high", "low", "close"]],
        new_df[["open_time_utc", "open", "high", "low", "close"]],
        on="open_time_utc",
        suffixes=("_existing", "_new"),
    )

    if len(overlap) == 0:
        return {"passed": True, "overlap_rows": 0, "details": None}

    deviations: list[dict] = []
    for col in ["open", "high", "low", "close"]:
        existing_col = overlap[f"{col}_existing"]
        new_col = overlap[f"{col}_new"]
        rel_dev = ((new_col - existing_col) / existing_col).abs()
        bad = rel_dev > threshold
        if bad.any():
            for idx in overlap.index[bad]:
                deviations.append({
                    "timestamp": str(overlap.loc[idx, "open_time_utc"]),
                    "field": col,
                    "existing": float(existing_col.loc[idx]),
                    "new": float(new_col.loc[idx]),
                    "relative_deviation": float(rel_dev.loc[idx]),
                })

    return {
        "passed": len(deviations) == 0,
        "overlap_rows": len(overlap),
        "details": deviations[:50] if deviations else None,
    }


def reconcile(
    existing_df: pd.DataFrame,
    new_df: pd.DataFrame,
    remove_partial: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """Merge existing and new OHLCV data with deduplication.

    Args:
        existing_df: Current canonical DataFrame.
        new_df: New rows to merge in.
        remove_partial: If True, remove the last candle if it appears partial
            (open_time + 1h > current UTC time).

    Returns:
        Tuple of (merged DataFrame, stats dict).
    """
    rows_before = len(existing_df)
    rows_new = len(new_df)

    # Block cross-venue merges (e.g. binance global + binanceus)
    venue_check = check_venue_compatibility(existing_df, new_df)
    if not venue_check["compatible"]:
        raise ValueError(venue_check["reason"])

    # Verify overlap prices match within 0.01% before merging
    overlap_result = verify_overlap(existing_df, new_df)
    if not overlap_result["passed"]:
        logger.warning(
            "Price deviation in %d overlap rows (threshold 0.01%%)",
            len(overlap_result["details"]),
        )

    # Concatenate
    combined = pd.concat([existing_df, new_df], ignore_index=True)

    # Sort by open_time_utc
    combined = combined.sort_values("open_time_utc").reset_index(drop=True)

    # Deduplicate on open_time_utc, keeping binance_vision source if conflict
    # Assign sort priority so binance_vision sorts first
    combined["_source_priority"] = combined["source"].map(SOURCE_PRIORITY).fillna(99)
    combined = combined.sort_values(
        ["open_time_utc", "_source_priority"]
    ).reset_index(drop=True)
    combined = combined.drop_duplicates(subset=["open_time_utc"], keep="first")
    combined = combined.drop(columns=["_source_priority"])
    combined = combined.sort_values("open_time_utc").reset_index(drop=True)

    rows_deduped = rows_before + rows_new - len(combined)

    # Remove partial candle at the end
    rows_trimmed = 0
    if remove_partial and len(combined) > 0:
        now_utc = pd.Timestamp.now(tz="UTC")
        last_open = combined["open_time_utc"].iloc[-1]
        candle_close = last_open + pd.Timedelta(hours=1)
        if candle_close > now_utc:
            combined = combined.iloc[:-1].reset_index(drop=True)
            rows_trimmed = 1
            logger.info("Removed partial candle at %s", last_open)

    # Check for gaps
    from ingestion.validators import check_no_gaps
    gap_result = check_no_gaps(combined)
    gaps_found = 0
    if not gap_result["passed"] and gap_result["details"]:
        gaps_found = gap_result["details"]["gaps_found"]

    stats = {
        "rows_before": rows_before,
        "rows_new": rows_new,
        "rows_deduped": rows_deduped,
        "rows_trimmed": rows_trimmed,
        "rows_after": len(combined),
        "gaps_found": gaps_found,
        "overlap_check": overlap_result,
    }

    return combined, stats


def main() -> int:
    """CLI entry point for reconciliation.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(description="Reconcile existing and new OHLCV data")
    parser.add_argument(
        "--existing", type=str, required=True, help="Path to existing canonical parquet"
    )
    parser.add_argument("--new", type=str, required=True, help="Path to new data parquet")
    parser.add_argument("--dry-run", action="store_true", help="Show stats but don't save")
    args = parser.parse_args()

    existing_path = Path(args.existing)
    new_path = Path(args.new)

    if not existing_path.exists():
        logger.error("Existing file not found: %s", existing_path)
        return 1
    if not new_path.exists():
        logger.error("New file not found: %s", new_path)
        return 1

    # Load data
    logger.info("Loading existing: %s", existing_path)
    existing_df = pd.read_parquet(existing_path)
    logger.info("  Existing rows: %d", len(existing_df))

    logger.info("Loading new: %s", new_path)
    new_df = pd.read_parquet(new_path)
    logger.info("  New rows: %d", len(new_df))

    # Reconcile
    merged_df, stats = reconcile(existing_df, new_df)

    # Log stats
    logger.info("Reconciliation stats:")
    logger.info("  Rows before:  %d", stats["rows_before"])
    logger.info("  Rows new:     %d", stats["rows_new"])
    logger.info("  Rows deduped: %d", stats["rows_deduped"])
    logger.info("  Rows trimmed: %d", stats["rows_trimmed"])
    logger.info("  Rows after:   %d", stats["rows_after"])
    logger.info("  Gaps found:   %d", stats["gaps_found"])

    # Validate merged data
    report = validate_ohlcv(merged_df)
    report["file_checked"] = str(existing_path)
    logger.info("Validation status: %s", report["overall_status"])

    # Save validation report (always, even on failure)
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    save_report(report, QUALITY_DIR, prefix="reconcile_validation")

    if args.dry_run:
        logger.info("Dry run — not saving")
        return 0

    # Block write on fatal validation failure
    if report["overall_status"] == "FAIL":
        logger.error(
            "Merged data FAILED validation — refusing to overwrite canonical file. "
            "Review quality report."
        )
        return 1

    # Archive current file only after validation passes
    archive_file(existing_path)

    # Save merged result
    merged_df.to_parquet(existing_path, engine="pyarrow", index=False)
    logger.info("Saved %d rows to %s", len(merged_df), existing_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
