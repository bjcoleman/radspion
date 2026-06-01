"""Test helpers and sample-agent constants (Testing Storyline seed)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "src" / "radspion" / "sql"

SAMPLE_AGENTS = {
    "alice": {
        "id": 1,
        "email": "alice@moravian.edu",
        "google_subject_id": "google-alice",
        "display_name": "Alice",
    },
    "bob": {
        "id": 2,
        "email": "bob@moravian.edu",
        "google_subject_id": "google-bob",
        "display_name": "Bob",
    },
    "charlie": {
        "id": 3,
        "email": "charlie@moravian.edu",
        "google_subject_id": "google-charlie",
        "display_name": "Charlie",
    },
    "diana": {
        "id": 4,
        "email": "diana@moravian.edu",
        "google_subject_id": "google-diana",
        "display_name": "Diana",
    },
}


def execute_sql_file(connection: sqlite3.Connection, sql_path: Path) -> None:
    """Run a SQL file against an open connection."""
    connection.executescript(sql_path.read_text(encoding="utf-8"))


def load_orientation_database(db_path: Path) -> None:
    """Schema + orientation seed (basic-training only)."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        execute_sql_file(conn, SQL_DIR / "schema.sql")
        execute_sql_file(conn, SQL_DIR / "seed_orientation.sql")
        conn.commit()


def load_testing_storyline_database(db_path: Path) -> None:
    """Schema + orientation + Testing Storyline acceptance seed."""
    load_orientation_database(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        execute_sql_file(conn, SQL_DIR / "seed_testing_storyline.sql")
        conn.commit()


def assert_mission_status(
    db_path: Path,
    *,
    user_id: int,
    slug: str,
    expected_status: str,
) -> None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT ams.status
            FROM agent_mission_status ams
            JOIN missions m ON m.id = ams.mission_id
            WHERE ams.user_id = ? AND m.slug = ?
            """,
            (user_id, slug),
        ).fetchone()
    assert row is not None, f"no status row for {slug}"
    assert row[0] == expected_status


def group_titles_in_order(html: str) -> list[str]:
    """Extract mission-group titles from dashboard HTML in document order."""
    import re

    return re.findall(r'class="mission-group__title">([^<]+)<', html)
