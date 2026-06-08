"""Tests for Agent Personnel File (read-only)."""

from pathlib import Path

import pytest

from radspion.app import create_app
from radspion.config import load_config
from radspion.database import DatabaseRadspionStorage
from radspion.personnel import format_personnel_date
from radspion.radspion import Radspion
from radspion.web.session_keys import SESSION_USER_ID
from tests.fakes.google_oauth import FakeGoogleOAuth
from tests.helpers import SAMPLE_AGENTS, load_testing_storyline_database


@pytest.fixture
def testing_storyline_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "storyline.db"
    load_testing_storyline_database(db_path)
    return db_path


def _client_for_db(db_path: Path):
    config = load_config(testing=True)
    storage = DatabaseRadspionStorage(db_path)
    radspion = Radspion(storage)
    oauth = FakeGoogleOAuth()
    app = create_app(config=config, radspion=radspion, oauth=oauth)
    return app.test_client()


def test_personnel_requires_login(testing_storyline_db: Path):
    client = _client_for_db(testing_storyline_db)

    response = client.get("/agent/personnel")

    assert response.status_code == 302
    assert response.location.endswith("/")


def test_personnel_page_shows_agent_record(testing_storyline_db: Path):
    client = _client_for_db(testing_storyline_db)
    alice = SAMPLE_AGENTS["alice"]
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = alice["id"]

    response = client.get("/agent/personnel")
    body = response.data.decode()

    assert response.status_code == 200
    assert 'class="page page--personnel"' in body
    assert "clearance-redeem.js" in body
    assert "Agent Personnel File" in body
    assert alice["display_name"] in body
    assert alice["email"] in body
    assert alice["codename"] in body
    assert 'href="/agent/personnel"' in body
    assert "site-header__agent-link--current" in body
    assert "Missions completed" in body
    assert "Active missions" in body
    assert body.count('<dd class="personnel-stats__value">2</dd>') == 2
    assert "Welcome to Radspion" in body
    assert "ES: Alpha" in body
    assert "Enlisted" in body
    assert "Personnel file opened" in body
    assert "Mission Completed" in body
    assert "Clearance Granted" in body
    assert "confidential_your_eyes_only.png" in body
    assert "personnel-codename.js" in body
    assert "data-personnel-codename-form" in body
    assert 'name="codename"' in body
    assert "readonly" not in body
    assert ">Update</button>" in body


def test_get_personnel_file_counts_and_service_record(testing_storyline_db: Path):
    storage = DatabaseRadspionStorage(testing_storyline_db)
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    personnel = storage.get_personnel_file(alice_id)

    assert personnel is not None
    assert personnel.display_name == SAMPLE_AGENTS["alice"]["display_name"]
    assert personnel.email == SAMPLE_AGENTS["alice"]["email"]
    assert personnel.codename == SAMPLE_AGENTS["alice"]["codename"]
    assert personnel.missions_completed == 2
    assert personnel.active_missions == 2
    assert personnel.service_record[0].verb in {
        "Mission Completed",
        "Clearance Granted",
        "Enlisted",
    }
    verbs = {entry.verb for entry in personnel.service_record}
    assert "Enlisted" in verbs
    assert "Mission Completed" in verbs
    assert "Clearance Granted" in verbs


def test_format_personnel_date():
    iso, label = format_personnel_date("2026-04-12 08:00:00")
    assert iso == "2026-04-12"
    assert label == "Apr 12, 2026"
