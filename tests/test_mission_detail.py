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


def test_active_mission_shows_brief_and_enabled_recovered_data_form(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.get("/agent/missions/es-beta")
    body = response.data.decode()

    assert response.status_code == 200
    assert "ES: Beta" in body
    assert "Mission Brief" in body
    assert "overview for the mission called ES: Beta" in body
    assert "recovered-data-form--multiline" in body
    assert 'data-mission-slug="es-beta"' in body
    assert 'name="completion_data"' in body
    assert "recovered-data-form__textarea" in body
    assert "Submit data" in body
    assert ">Recovered Data</h2>" in body
    assert body.count("mission-content-panel") == 1
    assert "mission-panel__header" in body
    assert "mission-panel__collapse" not in body
    assert "mission-group__chevron" not in body
    assert "Enter the data you recovered from this mission" in body
    assert "mission-detail-submit.js" in body
    assert 'id="recovered-data-input"' in body
    assert "disabled" not in body.split('id="recovered-data-input"')[1].split("</form>")[0]
    assert "recovered-data__value" not in body


def test_completed_mission_shows_recovered_data_debrief_and_brief(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.get("/agent/missions/es-alpha")
    body = response.data.decode()

    assert response.status_code == 200
    assert "ES: Alpha" in body
    assert body.count("mission-content-panel") == 2
    assert body.count("mission-panel__collapse") == 3
    before_recovered = body.split('id="recovered-data-heading"')[0]
    recovered_panel = before_recovered.rsplit("mission-panel__collapse", 1)[1]
    recovered_panel = recovered_panel.split("</details>")[0]
    assert " open" not in recovered_panel.split(">")[0]
    before_debrief = body.split('id="debrief-heading"')[0]
    debrief_panel = before_debrief.rsplit("mission-panel__collapse", 1)[1]
    debrief_panel = debrief_panel.split("</details>")[0]
    assert " open" in debrief_panel.split(">")[0]
    before_brief = body.split('id="brief-heading"')[0]
    brief_panel = before_brief.rsplit("mission-panel__collapse", 1)[1]
    brief_panel = brief_panel.split("</details>")[0]
    assert " open" not in brief_panel.split(">")[0]
    assert "recovered-data__value" in body
    assert "COMPLETE es-alpha" in body
    assert "Mission Debrief" in body
    assert "Congratulations, you completed ES: Alpha" in body
    assert "Mission Brief" in body
    assert "recovered-data-form" not in body


def test_mission_detail_404_when_not_listed(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.get("/agent/missions/es-alpha")
    assert response.status_code == 404
    assert "Transmission Terminated" in response.data.decode()
