"""Tests for granting clearance in storage."""

from radspion.database import DatabaseRadspionStorage
from radspion.radspion import Radspion
from tests.helpers import SAMPLE_AGENTS, assert_mission_status


def test_redeem_example_clearance_lists_two_missions_for_diana(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    result = testing_storyline_storage.grant_clearance(diana_id, "EXAMPLE-CLEARANCE")

    assert result.outcome == "success"
    assert len(result.new_missions) == 2
    slugs = {mission.slug for mission in result.new_missions}
    assert slugs == {"es-alpha", "es-beta"}
    assert all(mission.group_name == "Testing Storyline" for mission in result.new_missions)
    assert_mission_status(
        testing_storyline_storage,
        user_id=diana_id,
        slug="es-alpha",
        expected_status="active",
    )
    assert_mission_status(
        testing_storyline_storage,
        user_id=diana_id,
        slug="es-beta",
        expected_status="active",
    )


def test_redeem_trims_whitespace(testing_storyline_storage: DatabaseRadspionStorage):
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    result = Radspion(testing_storyline_storage).grant_clearance(
        diana_id,
        "  EXAMPLE-CLEARANCE  ",
    )

    assert result.outcome == "success"
    assert len(result.new_missions) == 2


def test_redeem_hidden_clearance_lists_one_mission(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    result = testing_storyline_storage.grant_clearance(diana_id, "HIDDEN-CLEARANCE")

    assert result.outcome == "success"
    assert len(result.new_missions) == 1
    assert result.new_missions[0].slug == "es-hidden"


def test_redeem_invalid_code(testing_storyline_storage: DatabaseRadspionStorage):
    result = testing_storyline_storage.grant_clearance(SAMPLE_AGENTS["diana"]["id"], "ZZ-INVALID")

    assert result.outcome == "invalid"
    assert result.new_missions == ()
    assert result.message is None


def test_redeem_case_sensitive(testing_storyline_storage: DatabaseRadspionStorage):
    result = testing_storyline_storage.grant_clearance(
        SAMPLE_AGENTS["diana"]["id"],
        "example-clearance",
    )

    assert result.outcome == "invalid"


def test_redeem_already_done_when_all_matching_listed(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    result = testing_storyline_storage.grant_clearance(alice_id, "EXAMPLE-CLEARANCE")

    assert result.outcome == "already_done"
    assert result.new_missions == ()
    assert result.message == "You have already been granted this clearance."


def test_redeem_already_done_for_bob_with_all_storyline_completed(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    result = testing_storyline_storage.grant_clearance(
        SAMPLE_AGENTS["bob"]["id"],
        "EXAMPLE-CLEARANCE",
    )

    assert result.outcome == "already_done"
