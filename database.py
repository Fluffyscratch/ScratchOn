"""
Database configuration and helper functions.
"""

import duckdb

# Database connection
db = duckdb.connect("ScratchOn_private/ScratchOn.duckdb")

# Initialize table
db.execute("""CREATE TABLE IF NOT EXISTS ScratchOn (
    serverid INTEGER PRIMARY KEY,
    language TEXT DEFAULT 'en',
    ai BOOLEAN DEFAULT FALSE,
    embeds BOOLEAN DEFAULT FALSE
)""")


def get_server_data(server_id: int, column_name: str):
    """
    Retrieves specific data from the 'ScratchOn' table in the 'ScratchOn.duckdb' database.

    :param server_id: The server ID to look for.
    :param column_name: The column name whose value is requested.
    :return: The value of the requested column for the given server ID, or None if not found.
    """
    try:
        query = f"SELECT {column_name} FROM ScratchOn WHERE serverid = ?"
        result = db.execute(query, [server_id]).fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def add_server(server_id: int):
    """
    Adds a new server entry to the database.

    :param server_id: The server ID to add.
    """
    db.execute(
        """
        INSERT INTO ScratchOn (serverid) VALUES (?)
    """,
        [server_id],
    )
