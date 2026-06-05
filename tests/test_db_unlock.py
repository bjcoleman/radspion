"""Tests for mission unlock code redemption in storage."""

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


def test_redeem_example_unlock_lists_two_missions_for_diana(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    result = storage.redeem_unlock_code(diana_id, "EXAMPLE-UNLOCK")

    assert result.outcome == "success"
    assert len(result.new_missions) == 2
    slugs = {mission.slug for mission in result.new_missions}
    assert slugs == {"es-alpha", "es-beta"}
    assert all(mission.group_name == "Testing Storyline" for mission in result.new_missions)
    assert_mission_status(storyline_db, user_id=diana_id, slug="es-alpha", expected_status="active")
    assert_mission_status(storyline_db, user_id=diana_id, slug="es-beta", expected_status="active")


def test_redeem_trims_whitespace(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    result = Radspion(storage).redeem_unlock_code(diana_id, "  EXAMPLE-UNLOCK  ")

    assert result.outcome == "success"
    assert len(result.new_missions) == 2


def test_redeem_hidden_unlock_lists_one_mission(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    result = storage.redeem_unlock_code(diana_id, "HIDDEN-UNLOCK")

    assert result.outcome == "success"
    assert len(result.new_missions) == 1
    assert result.new_missions[0].slug == "es-hidden"


def test_redeem_invalid_code(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    result = storage.redeem_unlock_code(SAMPLE_AGENTS["diana"]["id"], "ZZ-INVALID")

    assert result.outcome == "invalid"
    assert result.new_missions == ()
    assert result.message is None


def test_redeem_case_sensitive(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    result = storage.redeem_unlock_code(SAMPLE_AGENTS["diana"]["id"], "example-unlock")

    assert result.outcome == "invalid"


def test_redeem_already_done_when_all_matching_listed(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    result = storage.redeem_unlock_code(alice_id, "EXAMPLE-UNLOCK")

    assert result.outcome == "already_done"
    assert result.new_missions == ()
    assert result.message == "Those missions are already on your dashboard."


def test_redeem_already_done_for_bob_with_all_storyline_completed(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    result = storage.redeem_unlock_code(SAMPLE_AGENTS["bob"]["id"], "EXAMPLE-UNLOCK")

    assert result.outcome == "already_done"
