"""Reconcile existing and new funding-rate data into the canonical parquet.

Mirrors ingestion/reconcile.py for the 8h funding settlement series:
1. Archive the current canonical funding file (copy, before overwrite).
2. Load existing + new DataFrames.
3. Concatenate, sort, deduplicate on open_time_utc (prefer binance_vision).
4. Validate the merged result via validate_funding.
5. Save as the new canonical funding file.

Funding is a distinct file from OHLCV, so there is no cross-venue OHLCV
interaction here — only binance_vision (bulk) and ccxt_binance (incremental)
ever appear, and the source priority resolves any PK conflict.

Usage:
    python -m ingestion.funding_reconcile --existing data/raw/btcusdt_funding_8h.parquet --new data/raw/btcusdt_funding_8h_update.parquet
    python -m ingestion.funding_reconcile --existing data/raw/btcusdt_funding_8h.parquet --new data/raw/btcusdt_funding_8h_update.parquet --dry-run
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.validators import save_report, validate_funding

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
# "ccxt_binance" is the live incremental Binance global API.
SOURCE_PRIORITY = {"binance_vision": 0, "ccxt_binance": 1}


def archive_file(file_path: Path, archive_dir: Path = ARCHIVE_DIR) -> Path | None:
    """Archive the current canonical funding file before overwriting.

    Creates a timestamped copy in `archive_dir` (default data/raw/archive/).

    Args:
        file_path: Path to the canonical funding parquet file.
        archive_dir: Directory to write the timestamped snapshot to.

    Returns:
        Path to the archived file, or None if source doesn't exist.
    """
    if not file_path.exists():
        logger.warning("No file to archive: %s", file_path)
        return None

    archive_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    archive_path = archive_dir / archive_name

    # Copy (not move) — keep the original until merge succeeds.
    shutil.copy2(file_path, archive_path)
    logger.info("Archived %s -> %s", file_path.name, archive_path)
    return archive_path


def reconcile_funding(
    existing_df: pd.DataFrame,
    new_df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Merge existing and new funding data with source-priority deduplication.

    Args:
        existing_df: Current canonical funding DataFrame.
        new_df: New rows to merge in.

    Returns:
        Tuple of (merged DataFrame, stats dict). Output PK is unique + sorted.
    """
    rows_before = len(existing_df)
    rows_new = len(new_df)

    combined = pd.concat([existing_df, new_df], ignore_index=True)
    combined = combined.sort_values("open_time_utc").reset_index(drop=True)

    # Deduplicate on open_time_utc, keeping binance_vision over ccxt_binance.
    combined["_source_priority"] = combined["source"].map(SOURCE_PRIORITY).fillna(99)
    combined = combined.sort_values(
        ["open_time_utc", "_source_priority"]
    ).reset_index(drop=True)
    combined = combined.drop_duplicates(subset=["open_time_utc"], keep="first")
    combined = combined.drop(columns=["_source_priority"])
    combined = combined.sort_values("open_time_utc").reset_index(drop=True)

    rows_deduped = rows_before + rows_new - len(combined)

    stats = {
        "rows_before": rows_before,
        "rows_new": rows_new,
        "rows_deduped": rows_deduped,
        "rows_after": len(combined),
    }
    return combined, stats


def main() -> int:
    """CLI entry point for funding reconciliation.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(description="Reconcile existing and new funding data")
    parser.add_argument(
        "--existing", type=str, required=True, help="Path to existing canonical funding parquet"
    )
    parser.add_argument("--new", type=str, required=True, help="Path to new funding data parquet")
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

    logger.info("Loading existing: %s", existing_path)
    existing_df = pd.read_parquet(existing_path)
    logger.info("  Existing rows: %d", len(existing_df))

    logger.info("Loading new: %s", new_path)
    new_df = pd.read_parquet(new_path)
    logger.info("  New rows: %d", len(new_df))

    merged_df, stats = reconcile_funding(existing_df, new_df)

    logger.info("Reconciliation stats:")
    logger.info("  Rows before:  %d", stats["rows_before"])
    logger.info("  Rows new:     %d", stats["rows_new"])
    logger.info("  Rows deduped: %d", stats["rows_deduped"])
    logger.info("  Rows after:   %d", stats["rows_after"])

    report = validate_funding(merged_df)
    report["file_checked"] = str(existing_path)
    logger.info("Validation ok: %s", report["ok"])
    for err in report["errors"]:
        logger.error("  ERROR: %s", err)
    for warn in report["warnings"]:
        logger.warning("  WARN: %s", warn)

    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    save_report(report, QUALITY_DIR, prefix="funding_reconcile_validation")

    if args.dry_run:
        logger.info("Dry run — not saving")
        return 0

    if not report["ok"]:
        logger.error(
            "Merged data FAILED validation — refusing to overwrite canonical file. "
            "Review quality report."
        )
        return 1

    # Archive current file only after validation passes.
    archive_file(existing_path)

    # Atomic-promote: write to staging, then rename (mirrors funding_bulk_download).
    staging_path = existing_path.with_suffix(existing_path.suffix + ".staging")
    merged_df.to_parquet(staging_path, engine="pyarrow", index=False)
    staging_path.replace(existing_path)
    logger.info("Saved %d rows to %s", len(merged_df), existing_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
