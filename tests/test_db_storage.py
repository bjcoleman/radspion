"""Tests for DatabaseRadspionStorage."""

import sqlite3
from pathlib import Path

import pytest

from radspion.database import DatabaseError, DatabaseRadspionStorage

_VALID_CODE = "TEST-CODE-ONE"
_OTHER_CODE = "TEST-CODE-TWO"


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE registration_access_codes (code TEXT NOT NULL PRIMARY KEY)")
        conn.executemany(
            "INSERT INTO registration_access_codes (code) VALUES (?)",
            [(_VALID_CODE,), (_OTHER_CODE,)],
        )
        conn.commit()
    return path


def test_registration_code_exists_for_known_code(database_path: Path):
    storage = DatabaseRadspionStorage(database_path)

    assert storage.registration_code_exists(_VALID_CODE) is True
    assert storage.registration_code_exists(_OTHER_CODE) is True


def test_registration_code_exists_false_for_unknown(database_path: Path):
    storage = DatabaseRadspionStorage(database_path)

    assert storage.registration_code_exists("not-a-real-code") is False


def test_registration_code_exists_raises_database_error_when_table_missing(tmp_path: Path):
    path = tmp_path / "empty.db"
    path.touch()

    storage = DatabaseRadspionStorage(path)

    with pytest.raises(DatabaseError, match="Database error checking registration code"):
        storage.registration_code_exists(_VALID_CODE)


def test_closed_connection_raises_database_error_for_all_queries(tmp_path: Path):
    """Each wrapped method maps sqlite3.Error to DatabaseError when the connection is closed."""
    path = tmp_path / "closed.db"
    with sqlite3.connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE registration_access_codes (code TEXT NOT NULL PRIMARY KEY);
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

    storage = DatabaseRadspionStorage(path)
    storage._conn.close()

    operations = [
        (lambda: storage.registration_code_exists(_VALID_CODE), "registration code"),
        (lambda: storage.find_user_by_google_subject_id("sub-1"), "loading user"),
        (lambda: storage.find_user_by_email("agent@example.com"), "loading user"),
        (lambda: storage.find_user_by_id(1), "loading user"),
        (
            lambda: storage.create_user(
                email="agent@example.com",
                google_subject_id="sub-1",
                display_name="Agent",
            ),
            "creating user",
        ),
    ]

    for operation, message_fragment in operations:
        with pytest.raises(DatabaseError, match=message_fragment):
            operation()
