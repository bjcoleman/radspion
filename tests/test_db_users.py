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
            CREATE TABLE groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE group_members (
                user_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, group_id)
            );
            INSERT INTO groups (id, name) VALUES (1, 'Orientation');
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


def test_get_orientation_group_id(database_path: Path):
    storage = DatabaseRadspionStorage(database_path)

    assert storage.get_orientation_group_id() == 1


def test_add_group_member(database_path: Path):
    storage = DatabaseRadspionStorage(database_path)
    user = storage.create_user(
        email="agent@example.com",
        google_subject_id="sub-1",
        display_name="Agent One",
    )

    storage.add_group_member(user.id, 1)

    row = storage._conn.execute(
        "SELECT 1 FROM group_members WHERE user_id = ? AND group_id = ?",
        (user.id, 1),
    ).fetchone()
    assert row is not None
