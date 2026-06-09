"""Apply SQL scripts to SQLite connections."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def execute_sql_script(connection: sqlite3.Connection, sql: str) -> None:
    """Run a SQL script string (may contain multiple statements)."""
    connection.executescript(sql)


def execute_sql_file(connection: sqlite3.Connection, sql_path: Path) -> None:
    """Run a SQL file against an open connection."""
    execute_sql_script(connection, sql_path.read_text(encoding="utf-8"))
