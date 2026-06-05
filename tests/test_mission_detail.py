"""Tests for agent mission detail pages (UC-016 / UC-017)."""

from pathlib import Path

import pytest

from radspion.app import create_app
from radspion.config import load_config
from radspion.database import DatabaseRadspionStorage
from radspion.radspion import Radspion
from radspion.web.session_keys import SESSION_USER_ID
from tests.fakes.google_oauth import FakeGoogleOAuth
from tests.helpers import SAMPLE_AGENTS, load_testing_storyline_database


@pytest.fixture
def storyline_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "storyline.db"
    load_testing_storyline_database(db_path)
    return db_path


def _client_for_db(db_path: Path):
    config = load_config(testing=True)
    radspion = Radspion(DatabaseRadspionStorage(db_path))
    app = create_app(config=config, radspion=radspion, oauth=FakeGoogleOAuth())
    return app.test_client()


def test_active_mission_shows_brief_and_enabled_completion_form(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.get("/agent/missions/es-beta")
    body = response.data.decode()

    assert response.status_code == 200
    assert "ES: Beta" in body
    assert "Mission Brief" in body
    assert "overview for the mission called ES: Beta" in body
    assert "completion-form--multiline" in body
    assert 'data-mission-slug="es-beta"' in body
    assert 'name="completion_code"' in body
    assert "completion-form__textarea" in body
    assert "Submit data" in body
    assert ">Data</h2>" in body
    assert "mission-detail-submit.js" in body
    assert 'id="completion-code"' in body
    assert "disabled" not in body.split('id="completion-code"')[1].split("</form>")[0]
    assert "recovered-data__value" not in body


def test_completed_mission_shows_recovered_data_debrief_and_brief(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.get("/agent/missions/es-alpha")
    body = response.data.decode()

    assert response.status_code == 200
    assert "ES: Alpha" in body
    assert "recovered-data__value" in body
    assert "COMPLETE es-alpha" in body
    assert "Mission Debrief" in body
    assert "Congratulations, you completed ES: Alpha" in body
    assert "Mission Brief" in body
    assert "completion-form" not in body


def test_mission_detail_404_when_not_listed(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.get("/agent/missions/es-alpha")
    assert response.status_code == 404
    assert "Transmission Terminated" in response.data.decode()
