"""Tests for mission status sync (UC-012)."""

import sqlite3

from radspion.database import DatabaseRadspionStorage
from radspion.radspion import Radspion
from tests.helpers import assert_mission_status


def test_sync_inserts_basic_training_for_new_agent(
    testing_storyline_storage: DatabaseRadspionStorage,
    testing_storyline_db_path,
):
    app = Radspion(testing_storyline_storage)

    user = testing_storyline_storage.create_user(
        email="new-agent@example.com",
        google_subject_id="google-new",
        display_name="New Agent",
    )
    app.sync_mission_status(user.id)

    assert_mission_status(
        testing_storyline_storage,
        user_id=user.id,
        slug="basic-training",
        expected_status="active",
    )
    with sqlite3.connect(testing_storyline_db_path) as conn:
        row = conn.execute(
            """
            SELECT ams.listed_via
            FROM agent_mission_status ams
            JOIN missions m ON m.id = ams.mission_id
            WHERE ams.user_id = ? AND m.slug = 'basic-training'
            """,
            (user.id,),
        ).fetchone()
    assert row is not None
    assert row[0] == "open"


def test_sync_is_idempotent(
    testing_storyline_storage: DatabaseRadspionStorage,
    testing_storyline_db_path,
):
    app = Radspion(testing_storyline_storage)

    user = testing_storyline_storage.create_user(
        email="new-agent@example.com",
        google_subject_id="google-new",
        display_name="New Agent",
    )
    app.sync_mission_status(user.id)
    app.sync_mission_status(user.id)

    assert_mission_status(
        testing_storyline_storage,
        user_id=user.id,
        slug="basic-training",
        expected_status="active",
    )
    with sqlite3.connect(testing_storyline_db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM agent_mission_status WHERE user_id = ?",
            (user.id,),
        ).fetchone()[0]
    assert count == 1
