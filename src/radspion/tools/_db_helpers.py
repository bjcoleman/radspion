"""Shared helpers for database CLI tools."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from pathlib import Path

from radspion.project_paths import database_path, schema_path
from radspion.sql_utils import execute_sql_file


class DbToolError(Exception):
    """Invalid usage or failed database operation."""


def confirm_overwrite(db_path: Path, *, force: bool) -> None:
    """Remove an existing database file after optional confirmation."""
    if not db_path.is_file():
        return
    if not force:
        confirm = input(f"Warning: Database file already exists at {db_path}\nOverwrite? (y/n): ")
        if confirm.lower() != "y":
            print("Aborted.")
            raise SystemExit(0)
    db_path.unlink()


def create_schema_database(
    db_path: Path,
    *,
    force: bool,
    after_schema: Callable[[sqlite3.Connection], None] | None = None,
) -> None:
    """Create ``db_path`` with schema only, optionally running extra SQL."""
    if not schema_path().is_file():
        raise DbToolError(f"Missing {schema_path()}")

    confirm_overwrite(db_path, force=force)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        execute_sql_file(conn, schema_path())
        if after_schema is not None:
            after_schema(conn)
        conn.commit()


def assert_schema_present(db_path: Path) -> None:
    """Ensure the database exists and has the groups table."""
    if not db_path.is_file():
        raise DbToolError(
            f"Database not found at {db_path}\nCreate it first with create_empty_db",
        )

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='groups' LIMIT 1",
        ).fetchone()
    if row is None:
        raise DbToolError(
            f"Database at {db_path} has no schema (groups table missing).\n"
            "Run create_empty_db first.",
        )


def resolve_database_path() -> Path:
    """Return the configured database path or raise."""
    path = database_path()
    if not str(path).strip():
        raise DbToolError("DATABASE_PATH is empty in .env.")
    return path
