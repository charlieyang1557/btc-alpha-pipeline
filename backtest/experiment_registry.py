"""
SQLite experiment registry for tracking backtest runs.

Provides create, insert, query, and stats functions for the `runs` table
as defined in PHASE0_BLUEPRINT.md.

Usage:
    python -m backtest.experiment_registry --action create
    python -m backtest.experiment_registry --action list
    python -m backtest.experiment_registry --action stats
    python -m backtest.experiment_registry --action get --run-id <uuid>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

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
DEFAULT_DB_PATH = PROJECT_ROOT / "backtest" / "experiments.db"

CONFIG_FILES = [
    PROJECT_ROOT / "config" / "execution.yaml",
    PROJECT_ROOT / "config" / "environments.yaml",
    PROJECT_ROOT / "config" / "schemas.yaml",
]

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    run_type TEXT NOT NULL DEFAULT 'single_run',
    parent_run_id TEXT,
    strategy_name TEXT NOT NULL,
    strategy_source TEXT NOT NULL,
    git_commit TEXT,
    config_hash TEXT,
    data_snapshot_date TEXT,
    feature_version TEXT DEFAULT 'none',
    split_version TEXT,
    train_start TEXT,
    train_end TEXT,
    validation_start TEXT,
    validation_end TEXT,
    test_start TEXT,
    test_end TEXT,
    effective_start TEXT,
    warmup_bars INTEGER,
    initial_capital REAL,
    final_capital REAL,
    total_return REAL,
    sharpe_ratio REAL,
    max_drawdown REAL,
    max_drawdown_duration_hours REAL,
    total_trades INTEGER,
    win_rate REAL,
    avg_trade_duration_hours REAL,
    avg_trade_return REAL,
    profit_factor REAL,
    fee_model TEXT,
    notes TEXT,
    review_status TEXT DEFAULT 'pending',
    review_reason TEXT,
    batch_id TEXT,
    hypothesis_hash TEXT,
    regime_holdout_passed INTEGER,
    lifecycle_state TEXT,
    created_at_utc TEXT NOT NULL
)
"""

# Migration SQL — append-only list of (column_name, column_def) pairs
# applied via ``ALTER TABLE ... ADD COLUMN`` to bring an older database
# up to the current schema. SQLite does not support in-place column
# modification, so the migration is one-way and idempotent (columns
# already present are skipped). DO NOT remove or reorder entries; doing
# so would break upgrade paths from databases that stopped at an
# intermediate Phase 1A / 1B / 2A schema.
#
# - Phase 1A entries: original Phase 1A columns added on top of Phase 0.
# - Phase 2A D4 entries: orchestrator-facing columns. Of these,
#   ``feature_version`` was actually introduced earlier (D1) but is
#   re-listed here defensively in case a Phase 1B database predates it.
#   ``lifecycle_state`` is written by the D8 orchestrator, not by D4 —
#   the column is added now so D4 registry rows can coexist with D8
#   rows in the same table without further migrations.
MIGRATION_COLUMNS = [
    # --- Phase 1A ---
    ("run_type", "TEXT NOT NULL DEFAULT 'single_run'"),
    ("parent_run_id", "TEXT"),
    ("effective_start", "TEXT"),
    ("warmup_bars", "INTEGER"),
    ("initial_capital", "REAL"),
    ("final_capital", "REAL"),
    ("max_drawdown_duration_hours", "REAL"),
    ("avg_trade_return", "REAL"),
    ("profit_factor", "REAL"),
    # --- Phase 2A D4 ---
    ("feature_version", "TEXT DEFAULT 'none'"),
    ("batch_id", "TEXT"),
    ("hypothesis_hash", "TEXT"),
    # SQLite has no native BOOLEAN; INTEGER 0/1/NULL is the canonical
    # encoding. NULL means "regime holdout did not run for this row".
    ("regime_holdout_passed", "INTEGER"),
    ("lifecycle_state", "TEXT"),
]

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a connection to the experiment registry SQLite database.

    Args:
        db_path: Path to the database file. Defaults to backtest/experiments.db.

    Returns:
        sqlite3.Connection with row_factory set to sqlite3.Row.
    """
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def create_table(conn: sqlite3.Connection) -> None:
    """Create the runs table if it doesn't exist, then apply migrations.

    If the table already exists from an earlier phase, any missing
    columns from :data:`MIGRATION_COLUMNS` are added via
    ``ALTER TABLE ... ADD COLUMN``. SQLite supports ADD COLUMN but not
    in-place modification. This is idempotent — columns that already
    exist are silently skipped, so older Phase 1A rows are preserved
    untouched and newly-added Phase 2A columns default to NULL on
    existing rows.

    Args:
        conn: SQLite connection.
    """
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()

    # Migrate existing tables: add any missing columns
    cursor = conn.execute("PRAGMA table_info(runs)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    for col_name, col_def in MIGRATION_COLUMNS:
        if col_name not in existing_cols:
            conn.execute(f"ALTER TABLE runs ADD COLUMN {col_name} {col_def}")
            logger.info("Migrated: added column '%s' to runs table", col_name)

    conn.commit()
    logger.info("Ensured 'runs' table exists with Phase 2A D4 schema")


# ---------------------------------------------------------------------------
# Config hash
# ---------------------------------------------------------------------------


def compute_config_hash() -> str:
    """Compute SHA256 hash of execution.yaml + environments.yaml + schemas.yaml.

    Returns:
        Hex digest prefixed with 'sha256:'.
    """
    hasher = hashlib.sha256()
    for path in CONFIG_FILES:
        if path.exists():
            hasher.update(path.read_bytes())
    return f"sha256:{hasher.hexdigest()[:16]}"


def get_git_commit() -> str | None:
    """Get the current git short SHA.

    Returns:
        Short commit hash string, or None if not in a git repo.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def get_split_version() -> str:
    """Read the split version from config/environments.yaml.

    Returns:
        Version string (e.g. "v1").
    """
    env_path = PROJECT_ROOT / "config" / "environments.yaml"
    if env_path.exists():
        with open(env_path) as f:
            config = yaml.safe_load(f)
        return config.get("version", "unknown")
    return "unknown"


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------


def insert_run(conn: sqlite3.Connection, run_data: dict[str, Any]) -> str:
    """Insert a new experiment run into the registry.

    Auto-generates run_id (UUID), created_at_utc, git_commit, config_hash,
    and split_version if not provided.

    Args:
        conn: SQLite connection.
        run_data: Dict of column name → value. Required: strategy_name, strategy_source.

    Returns:
        The run_id of the inserted row.

    Raises:
        ValueError: If required fields are missing.
    """
    required = ["strategy_name", "strategy_source"]
    for field in required:
        if field not in run_data:
            raise ValueError(f"Missing required field: {field}")

    # Auto-fill defaults
    run_data.setdefault("run_id", str(uuid.uuid4()))
    run_data.setdefault("created_at_utc", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    run_data.setdefault("git_commit", get_git_commit())
    run_data.setdefault("config_hash", compute_config_hash())
    run_data.setdefault("split_version", get_split_version())
    run_data.setdefault("feature_version", "none")
    run_data.setdefault("review_status", "pending")

    columns = ", ".join(run_data.keys())
    placeholders = ", ".join(["?"] * len(run_data))
    values = list(run_data.values())

    conn.execute(f"INSERT INTO runs ({columns}) VALUES ({placeholders})", values)
    conn.commit()
    logger.info("Inserted run %s (strategy: %s)", run_data["run_id"], run_data["strategy_name"])
    return run_data["run_id"]


def get_run(conn: sqlite3.Connection, run_id: str) -> dict[str, Any] | None:
    """Retrieve a single run by its run_id.

    Args:
        conn: SQLite connection.
        run_id: UUID of the run to retrieve.

    Returns:
        Dict of run data, or None if not found.
    """
    cursor = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def list_runs(
    conn: sqlite3.Connection,
    strategy_name: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List experiment runs, optionally filtered by strategy name.

    Args:
        conn: SQLite connection.
        strategy_name: Filter to only this strategy (optional).
        limit: Maximum rows to return.

    Returns:
        List of run dicts, ordered by created_at_utc DESC.
    """
    if strategy_name:
        cursor = conn.execute(
            "SELECT * FROM runs WHERE strategy_name = ? ORDER BY created_at_utc DESC LIMIT ?",
            (strategy_name, limit),
        )
    else:
        cursor = conn.execute(
            "SELECT * FROM runs ORDER BY created_at_utc DESC LIMIT ?",
            (limit,),
        )
    return [dict(row) for row in cursor.fetchall()]


def get_stats(conn: sqlite3.Connection) -> dict[str, Any]:
    """Compute summary statistics across all experiment runs.

    Args:
        conn: SQLite connection.

    Returns:
        Dict with aggregate stats: total_runs, unique_strategies,
        avg_sharpe, avg_return, best/worst runs by Sharpe, etc.
    """
    stats: dict[str, Any] = {}

    # Total runs
    cursor = conn.execute("SELECT COUNT(*) as cnt FROM runs")
    stats["total_runs"] = cursor.fetchone()["cnt"]

    if stats["total_runs"] == 0:
        return stats

    # Unique strategies
    cursor = conn.execute("SELECT COUNT(DISTINCT strategy_name) as cnt FROM runs")
    stats["unique_strategies"] = cursor.fetchone()["cnt"]

    # Average metrics (excluding NULLs)
    cursor = conn.execute("""
        SELECT
            AVG(total_return) as avg_return,
            AVG(sharpe_ratio) as avg_sharpe,
            AVG(max_drawdown) as avg_drawdown,
            AVG(total_trades) as avg_trades,
            AVG(win_rate) as avg_win_rate,
            MIN(sharpe_ratio) as min_sharpe,
            MAX(sharpe_ratio) as max_sharpe,
            MIN(total_return) as min_return,
            MAX(total_return) as max_return,
            MAX(max_drawdown) as worst_drawdown
        FROM runs
        WHERE sharpe_ratio IS NOT NULL
    """)
    row = cursor.fetchone()
    if row:
        stats.update(dict(row))

    # Review status breakdown
    cursor = conn.execute("""
        SELECT review_status, COUNT(*) as cnt
        FROM runs
        GROUP BY review_status
    """)
    stats["review_breakdown"] = {r["review_status"]: r["cnt"] for r in cursor.fetchall()}

    # Per-strategy summary
    cursor = conn.execute("""
        SELECT
            strategy_name,
            COUNT(*) as run_count,
            AVG(sharpe_ratio) as avg_sharpe,
            MAX(sharpe_ratio) as best_sharpe,
            AVG(total_return) as avg_return
        FROM runs
        GROUP BY strategy_name
        ORDER BY avg_sharpe DESC
    """)
    stats["by_strategy"] = [dict(r) for r in cursor.fetchall()]

    return stats


def update_review(
    conn: sqlite3.Connection,
    run_id: str,
    status: str,
    reason: str | None = None,
) -> bool:
    """Update the review status of a run.

    Args:
        conn: SQLite connection.
        run_id: UUID of the run.
        status: New review status ("pending", "approved", "rejected").
        reason: Optional reason for the review decision.

    Returns:
        True if the run was found and updated, False otherwise.
    """
    valid_statuses = {"pending", "approved", "rejected"}
    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")

    cursor = conn.execute(
        "UPDATE runs SET review_status = ?, review_reason = ? WHERE run_id = ?",
        (status, reason, run_id),
    )
    conn.commit()
    updated = cursor.rowcount > 0
    if updated:
        logger.info("Updated run %s: review_status=%s", run_id, status)
    return updated


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point for experiment registry operations.

    Returns:
        Exit code: 0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(description="Experiment registry management")
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        choices=["create", "list", "stats", "get"],
        help="Action to perform",
    )
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB_PATH), help="Database path")
    parser.add_argument("--run-id", type=str, default=None, help="Run ID (for get action)")
    parser.add_argument("--strategy", type=str, default=None, help="Filter by strategy name")
    parser.add_argument("--limit", type=int, default=50, help="Max rows for list")
    args = parser.parse_args()

    db_path = Path(args.db)
    conn = get_connection(db_path)

    try:
        if args.action == "create":
            create_table(conn)
            logger.info("Database ready at %s", db_path)

        elif args.action == "list":
            create_table(conn)
            runs = list_runs(conn, strategy_name=args.strategy, limit=args.limit)
            if not runs:
                logger.info("No runs found")
            else:
                for run in runs:
                    print(
                        f"  {run['run_id'][:8]}  {run['strategy_name']:30s}  "
                        f"sharpe={run.get('sharpe_ratio', 'N/A'):>8}  "
                        f"return={run.get('total_return', 'N/A'):>8}  "
                        f"status={run.get('review_status', 'N/A')}"
                    )
                logger.info("Listed %d runs", len(runs))

        elif args.action == "stats":
            create_table(conn)
            stats = get_stats(conn)
            print(json.dumps(stats, indent=2, default=str))

        elif args.action == "get":
            if not args.run_id:
                logger.error("--run-id required for get action")
                return 1
            create_table(conn)
            run = get_run(conn, args.run_id)
            if run:
                print(json.dumps(run, indent=2, default=str))
            else:
                logger.error("Run not found: %s", args.run_id)
                return 1

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
