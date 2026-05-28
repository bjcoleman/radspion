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
