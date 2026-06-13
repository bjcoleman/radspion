"""Tests for DatabaseRadspionStorage."""

import sqlite3
from pathlib import Path

import pytest

from radspion.database import DatabaseError, DatabaseRadspionStorage
from radspion.radspion import Radspion


def test_agent_has_listed_mission_true_when_on_dashboard(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    user = testing_storyline_storage.create_user(
        email="agent@example.com",
        google_subject_id="sub-1",
        display_name="Agent",
    )
    Radspion(testing_storyline_storage).sync_mission_status(user.id)

    assert testing_storyline_storage.agent_has_listed_mission(user.id, "basic-training") is True


def test_agent_has_listed_mission_false_when_not_listed(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    user = testing_storyline_storage.create_user(
        email="agent@example.com",
        google_subject_id="sub-1",
        display_name="Agent",
    )
    Radspion(testing_storyline_storage).sync_mission_status(user.id)

    assert testing_storyline_storage.agent_has_listed_mission(user.id, "es-alpha") is False


@pytest.mark.parametrize(
    ("operation", "message_fragment"),
    [
        (lambda storage: storage.sync_mission_status(1), "syncing mission status"),
        (lambda storage: storage.get_agent_dashboard(1), "loading agent dashboard"),
        (
            lambda storage: storage.agent_has_listed_mission(1, "basic-training"),
            "checking mission list",
        ),
        (
            lambda storage: storage.find_listed_mission(1, "basic-training"),
            "loading mission",
        ),
        (
            lambda storage: storage.get_listed_mission_content(1, "basic-training"),
            "loading mission detail",
        ),
        (
            lambda storage: storage.grant_clearance(1, "EXAMPLE-CLEARANCE"),
            "granting clearance",
        ),
        (
            lambda storage: storage.submit_mission_data(1, "es-beta", "COMPLETE es-beta"),
            "submitting mission data",
        ),
    ],
)
def test_mission_queries_raise_database_error_when_tables_missing(
    tmp_path: Path,
    operation,
    message_fragment: str,
):
    path = tmp_path / "empty.db"
    path.touch()

    storage = DatabaseRadspionStorage(path)
    try:
        with pytest.raises(DatabaseError, match=message_fragment):
            operation(storage)
    finally:
        storage.close()


def test_closed_connection_raises_database_error_for_all_queries(tmp_path: Path):
    """Each wrapped method maps sqlite3.Error to DatabaseError when the connection is closed."""
    path = tmp_path / "closed.db"
    with sqlite3.connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                google_subject_id TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                codename TEXT NOT NULL UNIQUE,
                is_operator INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        conn.commit()

    storage = DatabaseRadspionStorage(path)
    storage.close()

    operations = [
        (lambda: storage.find_user_by_google_subject_id("sub-1"), "loading user"),
        (lambda: storage.find_user_by_email("agent@example.com"), "loading user"),
        (lambda: storage.find_user_by_id(1), "loading user"),
        (lambda: storage.find_user_by_codename("Field-Agent"), "loading user"),
        (lambda: storage.get_personnel_file(1), "loading personnel file"),
        (lambda: storage.get_field_activity(), "loading field activity"),
        (
            lambda: storage.create_user(
                email="agent@example.com",
                google_subject_id="sub-1",
                display_name="Agent",
            ),
            "creating user",
        ),
        (lambda: storage.sync_mission_status(1), "syncing mission status"),
        (lambda: storage.get_agent_dashboard(1), "loading agent dashboard"),
        (
            lambda: storage.agent_has_listed_mission(1, "basic-training"),
            "checking mission list",
        ),
        (lambda: storage.find_listed_mission(1, "basic-training"), "loading mission"),
        (
            lambda: storage.get_listed_mission_content(1, "basic-training"),
            "loading mission detail",
        ),
        (lambda: storage.grant_clearance(1, "EXAMPLE-CLEARANCE"), "granting clearance"),
        (
            lambda: storage.submit_mission_data(1, "es-beta", "COMPLETE es-beta"),
            "submitting mission data",
        ),
    ]

    for operation, message_fragment in operations:
        with pytest.raises(DatabaseError, match=message_fragment):
            operation()
