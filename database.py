"""Database configuration and helper functions."""

import logging
from pathlib import Path

import duckdb

log = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "private" / "ScratchOn.duckdb"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

db = duckdb.connect(str(DB_PATH))

db.execute("""
    CREATE TABLE IF NOT EXISTS ScratchOn (
        serverid BIGINT PRIMARY KEY,
        language TEXT DEFAULT 'en',
        embeds BOOLEAN DEFAULT FALSE
    )
""")

ALLOWED_COLUMNS = {"language", "embeds"}
DEFAULTS = {"language": "en", "embeds": False}


def get_server_data(server_id: int, column_name: str):
    """Return the value of `column_name` for a server, or the default if the server isn't registered."""
    if column_name not in ALLOWED_COLUMNS:
        raise ValueError(f"Invalid column: {column_name!r}")
    row = db.execute(
        f"SELECT {column_name} FROM ScratchOn WHERE serverid = ?", [server_id]
    ).fetchone()
    return row[0] if row else DEFAULTS[column_name]


def add_server(server_id: int) -> None:
    """Add a server with default settings; does nothing if it already exists."""
    db.execute(
        "INSERT INTO ScratchOn (serverid) VALUES (?) ON CONFLICT DO NOTHING",
        [server_id],
    )


def set_server_data(server_id: int, column_name: str, value) -> None:
    """Set a setting for a server, creating the row if needed."""
    if column_name not in ALLOWED_COLUMNS:
        raise ValueError(f"Invalid column: {column_name!r}")
    add_server(server_id)
    db.execute(
        f"UPDATE ScratchOn SET {column_name} = ? WHERE serverid = ?",
        [value, server_id],
    )