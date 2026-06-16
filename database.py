"""
Database configuration and helper functions.
"""

import logging

import duckdb

logger = logging.getLogger(__name__)

VALID_COLUMNS: set[str] = {"language", "ai", "embeds"}

# ---------------------------------------------------------------------------
# Connection and schema
# ---------------------------------------------------------------------------

db = duckdb.connect("private/ScratchOn.duckdb")

db.execute(
    """
    CREATE TABLE IF NOT EXISTS ScratchOn (
        serverid INTEGER PRIMARY KEY,
        language TEXT    DEFAULT 'en',
        ai       BOOLEAN DEFAULT FALSE,
        embeds   BOOLEAN DEFAULT FALSE
    )
    """
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_server_data(server_id: int, column_name: str) -> object | None:
    """
    Retrieve a single column value for *server_id*.

    :param server_id:  The Discord server ID to look up.
    :param column_name: Column whose value is requested (must be in VALID_COLUMNS).
    :return: The value, or ``None`` if not found or on error.
    """
    if column_name not in VALID_COLUMNS:
        logger.error("Rejected invalid column name: %s", column_name)
        return None

    try:
        result = db.execute(
            f"SELECT {column_name} FROM ScratchOn WHERE serverid = ?",
            [server_id],
        ).fetchone()
        return result[0] if result else None
    except Exception:
        logger.exception(
            "Failed to read column '%s' for server %s", column_name, server_id
        )
        return None


def add_server(server_id: int) -> None:
    """
    Insert a new server entry (idempotent — duplicates are ignored).

    :param server_id: The Discord server ID to add.
    """
    try:
        db.execute(
            "INSERT INTO ScratchOn (serverid) VALUES (?)",
            [server_id],
        )
    except Exception:
        logger.exception("Failed to insert server %s", server_id)
