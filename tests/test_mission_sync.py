"""Tests for mission status sync (UC-012)."""

from pathlib import Path

import pytest

from radspion.database import DatabaseRadspionStorage
from radspion.radspion import Radspion
from tests.helpers import assert_mission_status, load_orientation_database


@pytest.fixture
def orientation_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "orientation.db"
    load_orientation_database(db_path)
    return db_path


def test_sync_inserts_basic_training_for_new_agent(orientation_db: Path):
    storage = DatabaseRadspionStorage(orientation_db)
    app = Radspion(storage)

    user = storage.create_user(
        email="new-agent@example.com",
        google_subject_id="google-new",
        display_name="New Agent",
    )
    app.sync_mission_status(user.id)

    assert_mission_status(
        orientation_db,
        user_id=user.id,
        slug="basic-training",
        expected_status="active",
    )


def test_sync_is_idempotent(orientation_db: Path):
    import sqlite3

    storage = DatabaseRadspionStorage(orientation_db)
    app = Radspion(storage)

    user = storage.create_user(
        email="new-agent@example.com",
        google_subject_id="google-new",
        display_name="New Agent",
    )
    app.sync_mission_status(user.id)
    app.sync_mission_status(user.id)

    assert_mission_status(
        orientation_db,
        user_id=user.id,
        slug="basic-training",
        expected_status="active",
    )
    with sqlite3.connect(orientation_db) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM agent_mission_status WHERE user_id = ?",
            (user.id,),
        ).fetchone()[0]
    assert count == 1
