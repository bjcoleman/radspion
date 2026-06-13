"""Tests for mission completion submission in storage."""

from radspion.database import DatabaseRadspionStorage
from radspion.radspion import Radspion
from tests.helpers import SAMPLE_AGENTS, assert_mission_status


def test_submit_success_no_new_missions(testing_storyline_storage: DatabaseRadspionStorage):
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    result = testing_storyline_storage.submit_mission_data(alice_id, "es-beta", "COMPLETE es-beta")

    assert result is not None
    assert result.outcome == "success"
    assert result.new_missions == ()
    assert_mission_status(
        testing_storyline_storage,
        user_id=alice_id,
        slug="es-beta",
        expected_status="completed",
    )


def test_submit_success_lists_prerequisite_mission(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    charlie_id = SAMPLE_AGENTS["charlie"]["id"]

    result = testing_storyline_storage.submit_mission_data(
        charlie_id,
        "es-alpha",
        "COMPLETE es-alpha",
    )

    assert result is not None
    assert result.outcome == "success"
    assert len(result.new_missions) == 1
    assert result.new_missions[0].slug == "es-gamma"
    assert_mission_status(
        testing_storyline_storage,
        user_id=charlie_id,
        slug="es-alpha",
        expected_status="completed",
    )
    assert_mission_status(
        testing_storyline_storage,
        user_id=charlie_id,
        slug="es-gamma",
        expected_status="active",
    )


def test_submit_success_after_clearance_lists_gamma(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    testing_storyline_storage.grant_clearance(diana_id, "EXAMPLE-CLEARANCE")
    result = testing_storyline_storage.submit_mission_data(
        diana_id,
        "es-alpha",
        "COMPLETE es-alpha",
    )

    assert result is not None
    assert result.outcome == "success"
    assert {mission.slug for mission in result.new_missions} == {"es-gamma"}
    assert_mission_status(
        testing_storyline_storage,
        user_id=diana_id,
        slug="es-gamma",
        expected_status="active",
    )


def test_submit_success_lists_delta_when_prereqs_met(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    charlie_id = SAMPLE_AGENTS["charlie"]["id"]

    testing_storyline_storage.submit_mission_data(charlie_id, "es-alpha", "COMPLETE es-alpha")
    result = testing_storyline_storage.submit_mission_data(
        charlie_id,
        "es-gamma",
        "COMPLETE es-gamma",
    )

    assert result is not None
    assert result.outcome == "success"
    assert {mission.slug for mission in result.new_missions} == {"es-delta"}
    assert_mission_status(
        testing_storyline_storage,
        user_id=charlie_id,
        slug="es-delta",
        expected_status="active",
    )


def test_submit_invalid_code(testing_storyline_storage: DatabaseRadspionStorage):
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    result = testing_storyline_storage.submit_mission_data(alice_id, "es-beta", "WRONG")

    assert result is not None
    assert result.outcome == "invalid"
    assert_mission_status(
        testing_storyline_storage,
        user_id=alice_id,
        slug="es-beta",
        expected_status="active",
    )


def test_submit_case_sensitive(testing_storyline_storage: DatabaseRadspionStorage):
    result = testing_storyline_storage.submit_mission_data(
        SAMPLE_AGENTS["alice"]["id"],
        "es-beta",
        "complete es-beta",
    )

    assert result is not None
    assert result.outcome == "invalid"


def test_submit_already_done(testing_storyline_storage: DatabaseRadspionStorage):
    bob_id = SAMPLE_AGENTS["bob"]["id"]

    result = testing_storyline_storage.submit_mission_data(
        bob_id,
        "es-alpha",
        "COMPLETE es-alpha",
    )

    assert result is not None
    assert result.outcome == "already_done"
    assert result.new_missions == ()
    assert result.message == "This mission is already marked complete."


def test_submit_not_listed_returns_none(testing_storyline_storage: DatabaseRadspionStorage):
    result = testing_storyline_storage.submit_mission_data(
        SAMPLE_AGENTS["diana"]["id"],
        "es-alpha",
        "COMPLETE es-alpha",
    )

    assert result is None


def test_submit_trims_whitespace(testing_storyline_storage: DatabaseRadspionStorage):
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    result = Radspion(testing_storyline_storage).submit_mission_data(
        alice_id,
        "es-beta",
        "  COMPLETE es-beta  ",
    )

    assert result is not None
    assert result.outcome == "success"
