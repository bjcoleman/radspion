"""Tests for agent dashboard and mission detail stub."""

from pathlib import Path

import pytest

from radspion.app import create_app
from radspion.config import load_config
from radspion.database import DatabaseRadspionStorage
from radspion.radspion import Radspion
from radspion.web.session_keys import SESSION_USER_ID
from tests.fakes.google_oauth import FakeGoogleOAuth
from tests.helpers import (
    SAMPLE_AGENTS,
    group_titles_in_order,
    load_orientation_database,
    load_testing_storyline_database,
)


@pytest.fixture
def orientation_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "orientation.db"
    load_orientation_database(db_path)
    return db_path


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


def test_dashboard_lists_basic_training_after_sync(orientation_db: Path):
    storage = DatabaseRadspionStorage(orientation_db)
    user = storage.create_user(
        email="new-agent@example.com",
        google_subject_id="google-new",
        display_name="New Agent",
    )
    Radspion(storage).sync_mission_status(user.id)

    client = _client_for_db(orientation_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = user.id

    response = client.get("/agent/dashboard")
    body = response.data.decode()

    assert response.status_code == 200
    assert "Mission Dashboard" in body
    assert "Welcome to Radspion" in body
    assert "basic-training" in body
    assert "Orientation" in body


def test_dashboard_group_order_descending_group_id(testing_storyline_db: Path):
    client = _client_for_db(testing_storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.get("/agent/dashboard")
    titles = group_titles_in_order(response.data.decode())

    assert titles == ["Testing Storyline", "Orientation"]


def test_dashboard_includes_clearance_form_and_transmission_modal(testing_storyline_db: Path):
    client = _client_for_db(testing_storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    body = client.get("/agent/dashboard").data.decode()

    assert 'placeholder="Clearance code"' in body
    assert "Request Access" in body
    assert "clearance-form" in body
    assert "disabled" not in body.split("clearance-form")[1].split("</form>")[0]
    assert "data-transmission-modal" in body
    assert "clearance-form.js" in body
    assert "transmission-modal.js" in body
    assert 'name="clearance_code"' in body
    assert "clearance-redeem.js" in body


def test_clearance_then_dashboard_lists_storyline_missions(testing_storyline_db: Path):
    client = _client_for_db(testing_storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    clearance = client.post("/api/clearance", json={"clearance_code": "EXAMPLE-CLEARANCE"})
    assert clearance.status_code == 200
    assert clearance.get_json()["outcome"] == "success"

    body = client.get("/agent/dashboard").data.decode()
    assert "es-alpha" in body
    assert "es-beta" in body
    assert "Testing Storyline" in body
