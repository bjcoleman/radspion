"""Tests for loading mission detail content from storage."""

from radspion.database import DatabaseRadspionStorage
from tests.helpers import SAMPLE_AGENTS


def test_get_listed_mission_content_omits_completion_data_when_active(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    content = testing_storyline_storage.get_listed_mission_content(
        SAMPLE_AGENTS["alice"]["id"],
        "es-beta",
    )

    assert content is not None
    assert content.status == "active"
    assert content.completion_data is None
    assert "ES: Beta" in content.brief_markdown


def test_get_listed_mission_content_includes_completion_data_when_completed(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    content = testing_storyline_storage.get_listed_mission_content(
        SAMPLE_AGENTS["alice"]["id"],
        "es-alpha",
    )

    assert content is not None
    assert content.status == "completed"
    assert content.completion_data == "COMPLETE es-alpha"


def test_find_listed_mission_returns_dashboard_mission_when_listed(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    mission = testing_storyline_storage.find_listed_mission(
        SAMPLE_AGENTS["alice"]["id"],
        "es-alpha",
    )

    assert mission is not None
    assert mission.slug == "es-alpha"
    assert mission.title == "ES: Alpha"
    assert mission.status == "completed"


def test_find_listed_mission_none_when_not_listed(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    assert (
        testing_storyline_storage.find_listed_mission(SAMPLE_AGENTS["diana"]["id"], "es-alpha")
        is None
    )


def test_get_listed_mission_content_none_when_not_listed(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    assert (
        testing_storyline_storage.get_listed_mission_content(
            SAMPLE_AGENTS["diana"]["id"],
            "es-alpha",
        )
        is None
    )
