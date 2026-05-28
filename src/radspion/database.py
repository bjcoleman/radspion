"""SQLite connection and storage for Radspion."""

import sqlite3
from pathlib import Path


class DatabaseError(Exception):
    """Raised when the SQLite database cannot be opened or used."""


class DatabaseRadspionStorage:
    """Persist and load data using a SQLite database file."""

    def __init__(self, database_path: Path) -> None:
        try:
            self._conn = sqlite3.connect(database_path, check_same_thread=False)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Could not open database at {database_path}: {exc}") from exc
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def registration_code_exists(self, code: str) -> bool:
        """Return True when the code exists in registration_access_codes."""
        try:
            row = self._conn.execute(
                "SELECT 1 FROM registration_access_codes WHERE code = ?",
                (code,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error checking registration code: {exc}") from exc
        return row is not None
