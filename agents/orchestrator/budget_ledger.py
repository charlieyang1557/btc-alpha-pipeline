"""D6 Stage 1 — crash-safe pre-charge SQLite budget ledger.

The ledger enforces Phase 2B's hard budget caps ($20 per batch, $100 per
UTC calendar month) with a pre-charge pattern:

    1. BEFORE an API call, write a row with ``status='pending'`` and an
       upper-bound ``estimated_cost`` (e.g., max tokens × Sonnet rate).
       This row is IMMEDIATELY counted against the batch and monthly
       budgets.
    2. AFTER the call succeeds, call :meth:`finalize` which flips
       ``status`` to ``'completed'`` and writes the true
       ``actual_cost`` (possibly less than the estimate).
    3. If the process crashes between steps 1 and 2, the ``pending``
       row remains. Pending rows ALWAYS count as spent via
       ``COALESCE(actual_cost, estimated_cost)``. This is the entire
       point of the pattern: a crashed call is not a free retry.

DESIGN INVARIANT (pre-charge semantics):
Budget checks MUST run against ``COALESCE(actual_cost, estimated_cost)``
so a pending row is treated as fully spent at its upper bound. Any code
path that reads ``actual_cost`` alone and treats NULL as zero is a bug.
This invariant is enforced by the SQL in :meth:`monthly_spent_usd` and
:meth:`batch_spent_usd`, and by a dedicated simulated-crash test.

DESIGN INVARIANT (UTC calendar month):
"Month" is strictly a UTC calendar month — the window running from
``YYYY-MM-01T00:00:00Z`` (inclusive) to the first instant of the next
calendar month (exclusive). A rolling 30-day window is EXPLICITLY
forbidden by CLAUDE.md. The month boundary is computed in code, not
delegated to SQLite ``date()`` helpers, so the semantics are independent
of the SQLite build's date-function support.

DESIGN INVARIANT (no resume):
Per CLAUDE.md, crashed batches are NOT resumed. This ledger therefore
does NOT implement a "reconcile pending → completed from API history"
path. :meth:`mark_crashed` exists solely to annotate the ledger for
audit; the pre-charge continues to count against budget even after
``mark_crashed`` is called (by virtue of ``COALESCE`` including the
``crashed`` status too).

CONTRACT BOUNDARY: this module imports only stdlib. It MUST NOT import
``anthropic`` or any Proposer-specific symbol; the ledger is backend-
agnostic and records generic ``api_call_kind`` strings supplied by the
caller.
"""

from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


# ---------------------------------------------------------------------------
# Status constants
# ---------------------------------------------------------------------------

STATUS_PENDING = "pending"
STATUS_COMPLETED = "completed"
STATUS_CRASHED = "crashed"

VALID_STATUSES: tuple[str, ...] = (
    STATUS_PENDING,
    STATUS_COMPLETED,
    STATUS_CRASHED,
)


# Budget caps (per CLAUDE.md "Phase 2 Agent & Budget Rules").
BATCH_CAP_USD: float = 20.0
MONTHLY_CAP_USD: float = 100.0


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ledger (
    id                TEXT PRIMARY KEY,
    batch_id          TEXT NOT NULL,
    api_call_kind     TEXT NOT NULL,
    status            TEXT NOT NULL,
    estimated_cost    REAL NOT NULL,
    actual_cost       REAL,
    created_at_utc    TEXT NOT NULL,
    completed_at_utc  TEXT,
    notes             TEXT
);
CREATE INDEX IF NOT EXISTS idx_ledger_batch    ON ledger (batch_id);
CREATE INDEX IF NOT EXISTS idx_ledger_created  ON ledger (created_at_utc);
CREATE INDEX IF NOT EXISTS idx_ledger_status   ON ledger (status);
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso_z(dt: datetime) -> str:
    """Canonical ISO 8601 string with trailing ``Z``."""
    if dt.tzinfo is None:
        raise ValueError("refusing to serialize naive datetime")
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _month_bounds(now: datetime) -> tuple[str, str]:
    """Return ``(start_iso_z, end_iso_z)`` for the UTC calendar month of ``now``.

    ``start`` is ``YYYY-MM-01T00:00:00.000Z`` and ``end`` is the same for
    the *next* calendar month. The interval is half-open: ``[start, end)``.
    """
    if now.tzinfo is None:
        raise ValueError("refusing to compute month for naive datetime")
    now_utc = now.astimezone(timezone.utc)
    start = datetime(
        now_utc.year, now_utc.month, 1, 0, 0, 0, tzinfo=timezone.utc
    )
    if now_utc.month == 12:
        end = datetime(now_utc.year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    else:
        end = datetime(
            now_utc.year, now_utc.month + 1, 1, 0, 0, 0, tzinfo=timezone.utc
        )
    return _iso_z(start), _iso_z(end)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LedgerEntry:
    """One row of the ledger table."""

    id: str
    batch_id: str
    api_call_kind: str
    status: str
    estimated_cost: float
    actual_cost: float | None
    created_at_utc: str
    completed_at_utc: str | None
    notes: str | None


# ---------------------------------------------------------------------------
# BudgetLedger
# ---------------------------------------------------------------------------


class BudgetLedger:
    """Crash-safe SQLite pre-charge budget ledger.

    Instances are cheap — they hold only the database path; each method
    opens a short-lived connection. This keeps the ledger safe to share
    across threads/processes without per-instance locking (SQLite handles
    it at the file level).
    """

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(_SCHEMA_SQL)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def write_pending(
        self,
        *,
        batch_id: str,
        api_call_kind: str,
        estimated_cost_usd: float,
        now: datetime | None = None,
        notes: str | None = None,
    ) -> str:
        """Insert a pending row. Returns the ledger row ``id``.

        The caller MUST invoke :meth:`finalize` or :meth:`mark_crashed`
        on this id after the API call, using the returned value as the
        handle. If the process dies before either finalization call, the
        row remains ``pending`` and continues to count as spent at its
        ``estimated_cost_usd`` upper bound.
        """
        if estimated_cost_usd < 0:
            raise ValueError(
                f"estimated_cost_usd must be >= 0; got {estimated_cost_usd!r}"
            )
        row_id = str(uuid.uuid4())
        ts = _iso_z(now or _utc_now())
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO ledger "
                "(id, batch_id, api_call_kind, status, "
                " estimated_cost, actual_cost, "
                " created_at_utc, completed_at_utc, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    row_id,
                    batch_id,
                    api_call_kind,
                    STATUS_PENDING,
                    float(estimated_cost_usd),
                    None,
                    ts,
                    None,
                    notes,
                ),
            )
        return row_id

    def finalize(
        self,
        row_id: str,
        *,
        actual_cost_usd: float,
        now: datetime | None = None,
    ) -> None:
        """Transition a pending row to completed with the true cost.

        Raises:
            KeyError: if no row with ``row_id`` exists.
            ValueError: if the row is not in ``pending`` status (already
                finalized or crashed — double-finalize is a bug).
        """
        if actual_cost_usd < 0:
            raise ValueError(
                f"actual_cost_usd must be >= 0; got {actual_cost_usd!r}"
            )
        ts = _iso_z(now or _utc_now())
        with self._conn() as conn:
            row = conn.execute(
                "SELECT status FROM ledger WHERE id = ?", (row_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"ledger row not found: {row_id!r}")
            if row["status"] != STATUS_PENDING:
                raise ValueError(
                    f"cannot finalize row {row_id!r}: status is "
                    f"{row['status']!r}, expected {STATUS_PENDING!r}"
                )
            conn.execute(
                "UPDATE ledger SET status = ?, actual_cost = ?, "
                "completed_at_utc = ? WHERE id = ?",
                (STATUS_COMPLETED, float(actual_cost_usd), ts, row_id),
            )

    def mark_crashed(
        self,
        row_id: str,
        *,
        now: datetime | None = None,
        notes: str | None = None,
    ) -> None:
        """Annotate a pending row as crashed; its pre-charge still counts.

        Per CLAUDE.md, crashed batches are NOT resumed. This method is
        audit telemetry only — the row's ``estimated_cost`` remains part
        of the batch and monthly totals.
        """
        ts = _iso_z(now or _utc_now())
        with self._conn() as conn:
            row = conn.execute(
                "SELECT status, notes FROM ledger WHERE id = ?", (row_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"ledger row not found: {row_id!r}")
            if row["status"] != STATUS_PENDING:
                raise ValueError(
                    f"cannot mark_crashed row {row_id!r}: status is "
                    f"{row['status']!r}, expected {STATUS_PENDING!r}"
                )
            merged_notes = notes if row["notes"] is None else (
                f"{row['notes']}\n{notes}" if notes else row["notes"]
            )
            conn.execute(
                "UPDATE ledger SET status = ?, completed_at_utc = ?, "
                "notes = ? WHERE id = ?",
                (STATUS_CRASHED, ts, merged_notes, row_id),
            )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def batch_spent_usd(self, batch_id: str) -> float:
        """Return total spent on ``batch_id``, counting pending at estimate."""
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(COALESCE(actual_cost, estimated_cost)), 0) "
                "AS total FROM ledger WHERE batch_id = ?",
                (batch_id,),
            ).fetchone()
        return float(row["total"])

    def monthly_spent_usd(self, now: datetime | None = None) -> float:
        """Return total spent in the UTC calendar month containing ``now``.

        Pending and crashed rows count at their ``estimated_cost``;
        completed rows count at ``actual_cost``.
        """
        start, end = _month_bounds(now or _utc_now())
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(COALESCE(actual_cost, estimated_cost)), 0) "
                "AS total FROM ledger "
                "WHERE created_at_utc >= ? AND created_at_utc < ?",
                (start, end),
            ).fetchone()
        return float(row["total"])

    def batch_remaining_usd(
        self, batch_id: str, *, batch_cap_usd: float = BATCH_CAP_USD
    ) -> float:
        """Return remaining batch budget; negative if overspent."""
        return batch_cap_usd - self.batch_spent_usd(batch_id)

    def monthly_remaining_usd(
        self,
        *,
        now: datetime | None = None,
        monthly_cap_usd: float = MONTHLY_CAP_USD,
    ) -> float:
        """Return remaining monthly budget; negative if overspent."""
        return monthly_cap_usd - self.monthly_spent_usd(now=now)

    def can_afford(
        self,
        *,
        batch_id: str,
        estimated_cost_usd: float,
        now: datetime | None = None,
        batch_cap_usd: float = BATCH_CAP_USD,
        monthly_cap_usd: float = MONTHLY_CAP_USD,
    ) -> bool:
        """Pre-call gate: True iff both batch and monthly caps allow it.

        Strictly inclusive of the cap (``<= cap``); a call that lands
        exactly on the cap is permitted once.
        """
        if estimated_cost_usd < 0:
            raise ValueError(
                f"estimated_cost_usd must be >= 0; got {estimated_cost_usd!r}"
            )
        batch_after = self.batch_spent_usd(batch_id) + estimated_cost_usd
        monthly_after = self.monthly_spent_usd(now=now) + estimated_cost_usd
        return batch_after <= batch_cap_usd and monthly_after <= monthly_cap_usd

    def list_entries(
        self, *, batch_id: str | None = None
    ) -> list[LedgerEntry]:
        """Return rows sorted by ``created_at_utc`` ascending."""
        with self._conn() as conn:
            if batch_id is None:
                cur = conn.execute(
                    "SELECT * FROM ledger ORDER BY created_at_utc ASC"
                )
            else:
                cur = conn.execute(
                    "SELECT * FROM ledger WHERE batch_id = ? "
                    "ORDER BY created_at_utc ASC",
                    (batch_id,),
                )
            rows = cur.fetchall()
        return [
            LedgerEntry(
                id=r["id"],
                batch_id=r["batch_id"],
                api_call_kind=r["api_call_kind"],
                status=r["status"],
                estimated_cost=float(r["estimated_cost"]),
                actual_cost=(
                    float(r["actual_cost"])
                    if r["actual_cost"] is not None
                    else None
                ),
                created_at_utc=r["created_at_utc"],
                completed_at_utc=r["completed_at_utc"],
                notes=r["notes"],
            )
            for r in rows
        ]

    def pending_entries(
        self, *, batch_id: str | None = None
    ) -> list[LedgerEntry]:
        """Return rows with ``status='pending'`` (audit / crash-recovery view)."""
        return [e for e in self.list_entries(batch_id=batch_id)
                if e.status == STATUS_PENDING]


__all__ = [
    "BATCH_CAP_USD",
    "BudgetLedger",
    "LedgerEntry",
    "MONTHLY_CAP_USD",
    "STATUS_COMPLETED",
    "STATUS_CRASHED",
    "STATUS_PENDING",
    "VALID_STATUSES",
]
