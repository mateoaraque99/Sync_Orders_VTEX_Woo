import hashlib
import json
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/events.db")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA foreign_keys=ON;")
    return con


def init_db() -> None:
    with _connect() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                last_change TEXT NOT NULL,
                dedupe_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS order_snapshot (
                order_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                connected_with_woo INTEGER NOT NULL DEFAULT 0,
                woo_order_id TEXT,
                snapshot_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        con.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_order_snapshot_status_connected
            ON order_snapshot(status, connected_with_woo)
            """
        )

        con.commit()


def _dedupe_hash(order_id: str, last_change: str) -> str:
    raw = f"{order_id}:{last_change}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def store_event_if_new(order_id: str, last_change: str) -> tuple[bool, int | None]:
    dedupe_hash = _dedupe_hash(order_id, last_change)
    created_at = datetime.utcnow().isoformat()

    with _connect() as con:
        try:
            cur = con.execute(
                """
                INSERT INTO events (order_id, last_change, dedupe_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, last_change, dedupe_hash, created_at),
            )
            con.commit()
            return True, cur.lastrowid
        except sqlite3.IntegrityError:
            return False, None


def upsert_order_snapshot(
    order_id: str,
    status: str,
    snapshot: dict,
    connected_with_woo: bool = False,
    woo_order_id: str | None = None,
) -> None:
    updated_at = datetime.utcnow().isoformat()
    connected_int = 1 if connected_with_woo else 0
    snapshot_json = json.dumps(snapshot, ensure_ascii=False)

    with _connect() as con:
        con.execute(
            """
            INSERT INTO order_snapshot (order_id, status, connected_with_woo, woo_order_id, snapshot_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                status = excluded.status,
                connected_with_woo = excluded.connected_with_woo,
                woo_order_id = excluded.woo_order_id,
                snapshot_json = excluded.snapshot_json,
                updated_at = excluded.updated_at
            """,
            (order_id, status, connected_int, woo_order_id, snapshot_json, updated_at),
        )
        con.commit()


def get_order_snapshot(order_id: str) -> dict | None:
    with _connect() as con:
        cur = con.execute(
            """
            SELECT order_id, status, connected_with_woo, woo_order_id, snapshot_json, updated_at
            FROM order_snapshot
            WHERE order_id = ?
            """,
            (order_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        return {
            "order_id": row[0],
            "status": row[1],
            "connected_with_woo": bool(row[2]),
            "woo_order_id": row[3],
            "snapshot": json.loads(row[4]),
            "updated_at": row[5],
        }


def mark_connected_with_woo(order_id: str, woo_order_id: str) -> None:
    updated_at = datetime.utcnow().isoformat()
    with _connect() as con:
        con.execute(
            """
            UPDATE order_snapshot
            SET connected_with_woo = 1,
                woo_order_id = ?,
                updated_at = ?
            WHERE order_id = ?
            """,
            (woo_order_id, updated_at, order_id),
        )
        con.commit()
