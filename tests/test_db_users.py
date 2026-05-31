"""Tests for user persistence in DatabaseRadspionStorage."""

import sqlite3
from pathlib import Path

import pytest

from radspion.database import DatabaseRadspionStorage


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    path = tmp_path / "users.db"
    with sqlite3.connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                google_subject_id TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                is_operator INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        conn.commit()
    return path


def test_create_and_find_user(database_path: Path):
    storage = DatabaseRadspionStorage(database_path)

    created = storage.create_user(
        email="agent@example.com",
        google_subject_id="sub-1",
        display_name="Agent One",
    )

    assert created.id == 1
    assert storage.find_user_by_google_subject_id("sub-1") == created
    assert storage.find_user_by_email("agent@example.com") == created
    assert storage.find_user_by_id(1) == created
