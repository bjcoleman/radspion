"""Tests for POST /api/unlock."""

from pathlib import Path

import pytest

from radspion.web.api import INVALID_UNLOCK_MESSAGE
from radspion.web.session_keys import SESSION_USER_ID
from tests.helpers import SAMPLE_AGENTS, load_testing_storyline_database


@pytest.fixture
def storyline_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "storyline.db"
    load_testing_storyline_database(db_path)
    return db_path


def _client_for_db(db_path: Path):
    from radspion.app import create_app
    from radspion.config import load_config
    from radspion.database import DatabaseRadspionStorage
    from radspion.radspion import Radspion
    from tests.fakes.google_oauth import FakeGoogleOAuth

    config = load_config(testing=True)
    radspion = Radspion(DatabaseRadspionStorage(db_path))
    return create_app(config=config, radspion=radspion, oauth=FakeGoogleOAuth()).test_client()


def test_unlock_success_returns_new_missions(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/unlock", json={"unlock_code": "EXAMPLE UNLOCK"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "success"
    slugs = {mission["slug"] for mission in data["new_missions"]}
    assert slugs == {"es-alpha", "es-beta"}
    assert data["new_missions"][0]["group_name"] == "Testing Storyline"


def test_unlock_invalid_returns_message(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/unlock", json={"unlock_code": "ZZ-INVALID"})
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"outcome": "invalid", "message": INVALID_UNLOCK_MESSAGE}


def test_unlock_already_done(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.post("/api/unlock", json={"unlock_code": "EXAMPLE UNLOCK"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "already_done"
    assert data["new_missions"] == []
    assert "message" in data


def test_unlock_rejects_missing_code(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/unlock", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing unlock_code"}


def test_unlock_rejects_empty_code(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/unlock", json={"unlock_code": "   "})
    assert response.status_code == 400


def test_unlock_rejects_non_json_body(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post(
        "/api/unlock",
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing unlock_code"}


def test_unlock_requires_sign_in(storyline_db: Path):
    client = _client_for_db(storyline_db)

    response = client.post("/api/unlock", json={"unlock_code": "EXAMPLE UNLOCK"})
    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}
