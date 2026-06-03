"""Tests for unified field data submission in storage."""

import sqlite3
from pathlib import Path

import pytest

from radspion.database import DatabaseRadspionStorage
from radspion.radspion import Radspion
from tests.helpers import SAMPLE_AGENTS, assert_mission_status, load_testing_storyline_database


@pytest.fixture
def storyline_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "storyline.db"
    load_testing_storyline_database(db_path)
    return db_path


def test_submit_data_unlock_success(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    result = storage.submit_data(diana_id, "EXAMPLE UNLOCK")

    assert result.outcome == "success"
    assert result.kind == "list"
    assert result.mission_slug is None
    assert len(result.new_missions) == 2
    assert {mission.slug for mission in result.new_missions} == {"es-alpha", "es-beta"}


def test_submit_data_unlock_already_done(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    result = storage.submit_data(alice_id, "EXAMPLE UNLOCK")

    assert result.outcome == "already_done"
    assert result.kind is None
    assert result.new_missions == ()


def test_submit_data_unlock_invalid(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    result = storage.submit_data(SAMPLE_AGENTS["diana"]["id"], "ZZ-INVALID")

    assert result.outcome == "invalid"
    assert result.kind is None


def test_submit_data_complete_success(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    result = storage.submit_data(alice_id, "COMPLETE es-beta")

    assert result.outcome == "success"
    assert result.kind == "complete"
    assert result.mission_slug == "es-beta"
    assert result.new_missions == ()
    assert_mission_status(
        storyline_db, user_id=alice_id, slug="es-beta", expected_status="completed"
    )


def test_submit_data_complete_lists_prerequisite_mission(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    charlie_id = SAMPLE_AGENTS["charlie"]["id"]

    result = storage.submit_data(charlie_id, "COMPLETE es-alpha")

    assert result.outcome == "success"
    assert result.kind == "complete"
    assert result.mission_slug == "es-alpha"
    assert len(result.new_missions) == 1
    assert result.new_missions[0].slug == "es-gamma"


def test_submit_data_complete_after_unlock(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    storage.submit_data(diana_id, "EXAMPLE UNLOCK")
    result = storage.submit_data(diana_id, "COMPLETE es-alpha")

    assert result.outcome == "success"
    assert result.kind == "complete"
    assert result.mission_slug == "es-alpha"
    assert {mission.slug for mission in result.new_missions} == {"es-gamma"}


def test_submit_data_complete_invalid_when_not_listed(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    result = storage.submit_data(SAMPLE_AGENTS["diana"]["id"], "COMPLETE es-alpha")

    assert result.outcome == "invalid"
    assert result.kind is None


def test_submit_data_complete_invalid_wrong_code(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    result = storage.submit_data(alice_id, "WRONG")

    assert result.outcome == "invalid"
    assert_mission_status(storyline_db, user_id=alice_id, slug="es-beta", expected_status="active")


def test_submit_data_complete_already_done(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    bob_id = SAMPLE_AGENTS["bob"]["id"]

    result = storage.submit_data(bob_id, "COMPLETE es-alpha")

    assert result.outcome == "already_done"
    assert result.kind is None
    assert result.message == "This mission is already marked complete."


def test_submit_data_unlock_checked_before_completion(storyline_db: Path):
    """If a string exists in both tables, unlock resolution wins."""
    storage = DatabaseRadspionStorage(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    with sqlite3.connect(storyline_db) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            UPDATE mission_unlock_codes
            SET unlock_code = 'COMPLETE es-beta'
            WHERE mission_id = (SELECT id FROM missions WHERE slug = 'es-hidden')
            """
        )
        conn.commit()

    result = storage.submit_data(diana_id, "COMPLETE es-beta")

    assert result.outcome == "success"
    assert result.kind == "list"
    assert result.mission_slug is None
    assert len(result.new_missions) == 1
    assert result.new_missions[0].slug == "es-hidden"


def test_submit_data_trims_whitespace(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    result = Radspion(storage).submit_data(alice_id, "  COMPLETE es-beta  ")

    assert result.outcome == "success"
    assert result.kind == "complete"
    assert result.mission_slug == "es-beta"


def test_submit_data_unlock_lists_group_name(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    result = storage.submit_data(diana_id, "EXAMPLE UNLOCK")

    assert result.outcome == "success"
    assert all(mission.group_name == "Testing Storyline" for mission in result.new_missions)
    assert_mission_status(storyline_db, user_id=diana_id, slug="es-alpha", expected_status="active")
    assert_mission_status(storyline_db, user_id=diana_id, slug="es-beta", expected_status="active")


def test_submit_data_unlock_hidden_mission(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    result = storage.submit_data(diana_id, "HIDDEN UNLOCK")

    assert result.outcome == "success"
    assert result.kind == "list"
    assert len(result.new_missions) == 1
    assert result.new_missions[0].slug == "es-hidden"


def test_submit_data_unlock_case_sensitive(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    result = storage.submit_data(SAMPLE_AGENTS["diana"]["id"], "example unlock")

    assert result.outcome == "invalid"


def test_submit_data_unlock_already_done_message(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    result = storage.submit_data(SAMPLE_AGENTS["bob"]["id"], "EXAMPLE UNLOCK")

    assert result.outcome == "already_done"
    assert result.message == "Those missions are already on your dashboard."


def test_submit_data_unlock_trims_whitespace(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    result = Radspion(storage).submit_data(diana_id, "  EXAMPLE UNLOCK  ")

    assert result.outcome == "success"
    assert result.kind == "list"
    assert len(result.new_missions) == 2


def test_submit_data_complete_lists_delta_when_prereqs_met(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    charlie_id = SAMPLE_AGENTS["charlie"]["id"]

    storage.submit_data(charlie_id, "COMPLETE es-alpha")
    result = storage.submit_data(charlie_id, "COMPLETE es-gamma")

    assert result.outcome == "success"
    assert result.kind == "complete"
    assert {mission.slug for mission in result.new_missions} == {"es-delta"}
    assert_mission_status(
        storyline_db, user_id=charlie_id, slug="es-delta", expected_status="active"
    )


def test_submit_data_complete_case_sensitive(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    result = storage.submit_data(SAMPLE_AGENTS["alice"]["id"], "complete es-beta")

    assert result.outcome == "invalid"


def test_submit_data_to_api_dict_success_complete(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    result = storage.submit_data(alice_id, "COMPLETE es-beta")

    assert result.to_api_dict() == {
        "outcome": "success",
        "new_missions": [],
        "kind": "complete",
        "mission_slug": "es-beta",
    }
