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

DESIGN INVARIANT (backend_kind / call_role tagging):
Every ledger row MUST carry both ``backend_kind`` and ``call_role``.
These fields let downstream rollups split D6 proposer spend from D7b
critic spend without parsing free-form ``api_call_kind`` strings.
``write_pending`` REQUIRES both fields explicitly. There is no default:
a caller that forgets to pass them raises ``TypeError``. Pre-Stage-2a
rows are backfilled once at schema-migration time with
``backend_kind='d6_proposer'``, ``call_role='propose'``; the backfill
is idempotent and runs exactly once per database via
:func:`_migrate_backend_kind_call_role`.
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


# backend_kind / call_role canonical vocabularies. These are enforced at
# write time; unknown values are rejected so the rollups never silently
# see a new category.
BACKEND_KIND_D6_PROPOSER = "d6_proposer"
BACKEND_KIND_D7B_CRITIC = "d7b_critic"
VALID_BACKEND_KINDS: tuple[str, ...] = (
    BACKEND_KIND_D6_PROPOSER,
    BACKEND_KIND_D7B_CRITIC,
)

CALL_ROLE_PROPOSE = "propose"
CALL_ROLE_CRITIQUE = "critique"
VALID_CALL_ROLES: tuple[str, ...] = (
    CALL_ROLE_PROPOSE,
    CALL_ROLE_CRITIQUE,
)


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ledger (
    id                TEXT PRIMARY KEY,
    batch_id          TEXT NOT NULL,
    api_call_kind     TEXT NOT NULL,
    backend_kind      TEXT NOT NULL,
    call_role         TEXT NOT NULL,
    status            TEXT NOT NULL,
    estimated_cost    REAL NOT NULL,
    actual_cost       REAL,
    created_at_utc    TEXT NOT NULL,
    completed_at_utc  TEXT,
    notes             TEXT
);
CREATE INDEX IF NOT EXISTS idx_ledger_batch         ON ledger (batch_id);
CREATE INDEX IF NOT EXISTS idx_ledger_created       ON ledger (created_at_utc);
CREATE INDEX IF NOT EXISTS idx_ledger_status        ON ledger (status);
"""


def _migrate_backend_kind_call_role(conn: sqlite3.Connection) -> None:
    """Idempotent migration: add ``backend_kind`` / ``call_role`` columns.

    Pre-Stage-2a ledgers have the ``ledger`` table but lack these two
    columns. Running this migration:

    1. Detects whether the columns already exist via ``PRAGMA table_info``.
    2. Adds the missing column(s) WITHOUT the ``NOT NULL`` constraint
       (SQLite cannot retrofit ``NOT NULL`` on an existing populated
       column without a full table rebuild, which we avoid to keep the
       migration in-place and reversible).
    3. Backfills NULL values with ``d6_proposer`` / ``propose``.
    4. Creates the two indexes if absent.

    After migration, application code REQUIRES both fields in
    ``write_pending`` via keyword arguments — the NOT NULL invariant is
    upheld at the application layer for pre-existing databases and at
    both layers for newly created ones (``_SCHEMA_SQL`` declares them
    ``NOT NULL``).
    """
    cols = {row[1] for row in conn.execute("PRAGMA table_info(ledger)")}
    if "backend_kind" not in cols:
        conn.execute("ALTER TABLE ledger ADD COLUMN backend_kind TEXT")
        conn.execute(
            "UPDATE ledger SET backend_kind = ? WHERE backend_kind IS NULL",
            (BACKEND_KIND_D6_PROPOSER,),
        )
    if "call_role" not in cols:
        conn.execute("ALTER TABLE ledger ADD COLUMN call_role TEXT")
        conn.execute(
            "UPDATE ledger SET call_role = ? WHERE call_role IS NULL",
            (CALL_ROLE_PROPOSE,),
        )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_ledger_backend_kind "
        "ON ledger (backend_kind)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_ledger_call_role "
        "ON ledger (call_role)"
    )


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
    backend_kind: str
    call_role: str
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
            _migrate_backend_kind_call_role(conn)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def write_pending(
        self,
        *,
        batch_id: str,
        api_call_kind: str,
        backend_kind: str,
        call_role: str,
        estimated_cost_usd: float,
        now: datetime | None = None,
        notes: str | None = None,
    ) -> str:
        """Insert a pending row. Returns the ledger row ``id``.

        ``backend_kind`` MUST be one of :data:`VALID_BACKEND_KINDS` and
        ``call_role`` MUST be one of :data:`VALID_CALL_ROLES`. Both are
        required keyword arguments with no default: every call site is
        explicit about which subsystem (D6 proposer vs. D7b critic) is
        charging the ledger. This is what makes the split cost rollup
        (:meth:`cost_by_backend_kind`) trustworthy.

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
        if backend_kind not in VALID_BACKEND_KINDS:
            raise ValueError(
                f"backend_kind must be one of {VALID_BACKEND_KINDS!r}; "
                f"got {backend_kind!r}"
            )
        if call_role not in VALID_CALL_ROLES:
            raise ValueError(
                f"call_role must be one of {VALID_CALL_ROLES!r}; "
                f"got {call_role!r}"
            )
        row_id = str(uuid.uuid4())
        ts = _iso_z(now or _utc_now())
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO ledger "
                "(id, batch_id, api_call_kind, backend_kind, call_role, "
                " status, estimated_cost, actual_cost, "
                " created_at_utc, completed_at_utc, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    row_id,
                    batch_id,
                    api_call_kind,
                    backend_kind,
                    call_role,
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
                backend_kind=r["backend_kind"],
                call_role=r["call_role"],
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

    def cost_by_backend_kind(
        self, *, batch_id: str | None = None
    ) -> dict[str, float]:
        """Return per-``backend_kind`` cost rollup for this ledger.

        Pending and crashed rows count at their ``estimated_cost``;
        completed rows count at ``actual_cost`` (via ``COALESCE``).
        Every ``backend_kind`` in :data:`VALID_BACKEND_KINDS` appears in
        the returned dict, defaulting to ``0.0`` when absent. This gives
        downstream callers a stable shape regardless of whether the
        batch issued any critic calls yet.
        """
        sql = (
            "SELECT backend_kind, "
            "COALESCE(SUM(COALESCE(actual_cost, estimated_cost)), 0) AS total "
            "FROM ledger "
        )
        params: tuple = ()
        if batch_id is not None:
            sql += "WHERE batch_id = ? "
            params = (batch_id,)
        sql += "GROUP BY backend_kind"
        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
        out: dict[str, float] = {k: 0.0 for k in VALID_BACKEND_KINDS}
        for r in rows:
            out[r["backend_kind"]] = float(r["total"])
        return out


__all__ = [
    "BACKEND_KIND_D6_PROPOSER",
    "BACKEND_KIND_D7B_CRITIC",
    "BATCH_CAP_USD",
    "BudgetLedger",
    "CALL_ROLE_CRITIQUE",
    "CALL_ROLE_PROPOSE",
    "LedgerEntry",
    "MONTHLY_CAP_USD",
    "STATUS_COMPLETED",
    "STATUS_CRASHED",
    "STATUS_PENDING",
    "VALID_BACKEND_KINDS",
    "VALID_CALL_ROLES",
    "VALID_STATUSES",
]
