"""Tests for loading mission detail content from storage."""

from pathlib import Path

import pytest

from radspion.database import DatabaseRadspionStorage
from tests.helpers import SAMPLE_AGENTS, load_testing_storyline_database


@pytest.fixture
def storyline_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "storyline.db"
    load_testing_storyline_database(db_path)
    return db_path


def test_get_listed_mission_content_omits_completion_code_when_active(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    content = storage.get_listed_mission_content(SAMPLE_AGENTS["alice"]["id"], "es-beta")

    assert content is not None
    assert content.status == "active"
    assert content.completion_code is None
    assert "ES: Beta" in content.brief_markdown


def test_get_listed_mission_content_includes_completion_code_when_completed(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    content = storage.get_listed_mission_content(SAMPLE_AGENTS["alice"]["id"], "es-alpha")

    assert content is not None
    assert content.status == "completed"
    assert content.completion_code == "COMPLETE es-alpha"


def test_find_listed_mission_returns_dashboard_mission_when_listed(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    mission = storage.find_listed_mission(SAMPLE_AGENTS["alice"]["id"], "es-alpha")

    assert mission is not None
    assert mission.slug == "es-alpha"
    assert mission.title == "ES: Alpha"
    assert mission.status == "completed"


def test_find_listed_mission_none_when_not_listed(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    assert storage.find_listed_mission(SAMPLE_AGENTS["diana"]["id"], "es-alpha") is None


def test_get_listed_mission_content_none_when_not_listed(storyline_db: Path):
    storage = DatabaseRadspionStorage(storyline_db)

    assert storage.get_listed_mission_content(SAMPLE_AGENTS["diana"]["id"], "es-alpha") is None
