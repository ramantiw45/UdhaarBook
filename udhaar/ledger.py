"""The ledger itself. SQLite, one file, no server, no account.

Deliberately boring: a shopkeeper's book should be a file they own, that
opens with any tool, on a machine under their counter.
"""

from __future__ import annotations

import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

DEFAULT_DB = os.getenv("UDHAAR_DB", "data/udhaar.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    name_key    TEXT    NOT NULL,
    amount      REAL    NOT NULL,
    direction   TEXT    NOT NULL CHECK (direction IN ('udhaar', 'payment')),
    note        TEXT    NOT NULL DEFAULT '',
    txn_date    TEXT    NOT NULL DEFAULT '',
    lane        TEXT    NOT NULL DEFAULT '',
    scan_id     INTEGER,
    created_at  TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entries_name_key ON entries(name_key);
CREATE INDEX IF NOT EXISTS idx_entries_scan    ON entries(scan_id);

CREATE TABLE IF NOT EXISTS scans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    backend     TEXT    NOT NULL DEFAULT '',
    lane        TEXT    NOT NULL DEFAULT '',
    ocr_text    TEXT    NOT NULL DEFAULT '',
    page_name   TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL
);
"""


def name_key(name: str) -> str:
    """Group 'Ramesh  Patil' and 'ramesh patil' onto the same customer."""
    cleaned = re.sub(r"[^\w\s]", "", name, flags=re.UNICODE)
    return re.sub(r"\s+", " ", cleaned).strip().lower()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    path = Path(db_path)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def connection(db_path: str = DEFAULT_DB) -> Iterator[sqlite3.Connection]:
    """Commit on the way out and actually close the file.

    Windows will not delete a database file with a live handle, which is how
    the test suite found this: the ledger worked, but it never let go.
    """
    conn = connect(db_path)
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db(db_path: str = DEFAULT_DB) -> None:
    with connection(db_path) as conn:
        conn.executescript(_SCHEMA)


def start_scan(backend: str, lane: str, ocr_text: str, page_name: str = "", db_path: str = DEFAULT_DB) -> int:
    with connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO scans (backend, lane, ocr_text, page_name, created_at) VALUES (?,?,?,?,?)",
            (backend, lane, ocr_text, page_name, _now()),
        )
        return int(cur.lastrowid)


def save_rows(rows: list[dict], lane: str = "", scan_id: int | None = None, db_path: str = DEFAULT_DB) -> int:
    """Insert confirmed rows. The reviewer has already approved these."""
    saved = 0
    with connection(db_path) as conn:
        for row in rows:
            name = str(row.get("name", "")).strip()
            key = name_key(name)
            if not name or not key:
                continue
            try:
                amount = float(row.get("amount", 0) or 0)
            except (TypeError, ValueError):
                continue
            if amount <= 0:
                continue
            direction = "payment" if str(row.get("direction", "")).lower() == "payment" else "udhaar"
            conn.execute(
                """INSERT INTO entries
                   (name, name_key, amount, direction, note, txn_date, lane, scan_id, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    name,
                    key,
                    round(amount, 2),
                    direction,
                    str(row.get("note", "") or "").strip(),
                    str(row.get("date", "") or "").strip(),
                    lane,
                    scan_id,
                    _now(),
                ),
            )
            saved += 1
    return saved


def balances(db_path: str = DEFAULT_DB) -> list[dict]:
    """Per customer: how much was given, how much came back, what is left."""
    with connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
                name_key,
                MAX(name)                                                   AS name,
                SUM(CASE WHEN direction = 'udhaar'  THEN amount ELSE 0 END)  AS given,
                SUM(CASE WHEN direction = 'payment' THEN amount ELSE 0 END)  AS received,
                COUNT(*)                                                    AS entries,
                MAX(txn_date)                                               AS last_date,
                MAX(scan_id)                                                AS page_no
            FROM entries
            GROUP BY name_key
            ORDER BY (SUM(CASE WHEN direction = 'udhaar' THEN amount ELSE 0 END)
                    - SUM(CASE WHEN direction = 'payment' THEN amount ELSE 0 END)) DESC
            """
        ).fetchall()

    out = []
    for row in rows:
        given = round(row["given"] or 0, 2)
        received = round(row["received"] or 0, 2)
        out.append(
            {
                "name": row["name"],
                "name_key": row["name_key"],
                "given": given,
                "received": received,
                "balance": round(given - received, 2),
                "entries": row["entries"],
                "last_date": row["last_date"] or "",
                "page_no": row["page_no"],
            }
        )
    return out


def totals(db_path: str = DEFAULT_DB) -> dict:
    with connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT
              COUNT(*)                                                    AS entries,
              COUNT(DISTINCT name_key)                                    AS customers,
              SUM(CASE WHEN direction = 'udhaar'  THEN amount ELSE 0 END) AS given,
              SUM(CASE WHEN direction = 'payment' THEN amount ELSE 0 END) AS received
            FROM entries
            """
        ).fetchone()

    given = round(row["given"] or 0, 2)
    received = round(row["received"] or 0, 2)
    return {
        "entries": row["entries"] or 0,
        "customers": row["customers"] or 0,
        "given": given,
        "received": received,
        "outstanding": round(given - received, 2),
    }


def entries_for(name_key_value: str, db_path: str = DEFAULT_DB) -> list[dict]:
    with connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM entries WHERE name_key = ? ORDER BY id ASC", (name_key_value,)
        ).fetchall()
    return [dict(row) for row in rows]


def recent(limit: int = 25, db_path: str = DEFAULT_DB) -> list[dict]:
    with connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM entries ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def reset(db_path: str = DEFAULT_DB) -> None:
    """Wipe the demo book. Used by tests and by the 'start over' button."""
    with connection(db_path) as conn:
        conn.execute("DELETE FROM entries")
        conn.execute("DELETE FROM scans")
