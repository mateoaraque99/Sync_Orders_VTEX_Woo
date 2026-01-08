import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/events.db")


def _connect() -> sqlite3.Connection:
    """
    Opens a connection to the SQLite database.

    - Creates the parent folder if it does not exist.
    - If the database file does not exist, SQLite creates it automatically.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """
    Initializes the database structure.

    This function:
    - Is meant to be called once when the Flask app starts.
    - Creates the 'events' table if it does not already exist.
    - Does NOT recreate or wipe existing data.
    """
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
        con.commit()


def _dedupe_hash(order_id: str, last_change: str) -> str:
    """
    Generates a unique hash for a specific order state.

    The combination of:
    - order_id
    - last_change

    uniquely represents a single event version coming from VTEX.
    """
    # Unique hash per order state
    raw = f"{order_id}:{last_change}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def store_event_if_new(order_id: str, last_change: str) -> tuple[bool, int | None]:
    """
    Stores the event only if it has not been processed before.

    This is the deduplication gate.

    Returns:
    - (True, event_id)  -> when the event is new and stored
    - (False, None)     -> when the event is a duplicate
    """
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
            # The UNIQUE constraint on dedupe_hash was violated
            # This means the event was already processed
            return False, None
