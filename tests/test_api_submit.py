"""Tests for POST /api/missions/<slug>/submit."""

from pathlib import Path

import pytest

from radspion.web.api import INVALID_SUBMIT_MESSAGE
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


def test_submit_success(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.post(
        "/api/missions/es-beta/submit",
        json={"completion_data": "COMPLETE es-beta"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "success"
    assert data["new_missions"] == []


def test_submit_success_with_new_missions(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["charlie"]["id"]

    response = client.post(
        "/api/missions/es-alpha/submit",
        json={"completion_data": "COMPLETE es-alpha"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "success"
    assert len(data["new_missions"]) == 1
    assert data["new_missions"][0]["slug"] == "es-gamma"


def test_submit_invalid_returns_message(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.post(
        "/api/missions/es-beta/submit",
        json={"completion_data": "WRONG"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"outcome": "invalid", "message": INVALID_SUBMIT_MESSAGE}


def test_submit_already_done(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["bob"]["id"]

    response = client.post(
        "/api/missions/es-alpha/submit",
        json={"completion_data": "COMPLETE es-alpha"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "already_done"
    assert data["new_missions"] == []
    assert "message" in data


def test_submit_not_listed_returns_404(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post(
        "/api/missions/es-alpha/submit",
        json={"completion_data": "COMPLETE es-alpha"},
    )
    assert response.status_code == 404


def test_submit_rejects_missing_code(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.post("/api/missions/es-beta/submit", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing completion_data"}


def test_submit_rejects_empty_code(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.post(
        "/api/missions/es-beta/submit",
        json={"completion_data": "   "},
    )
    assert response.status_code == 400


def test_submit_rejects_non_json_body(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.post(
        "/api/missions/es-beta/submit",
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing completion_data"}


def test_submit_requires_sign_in(storyline_db: Path):
    client = _client_for_db(storyline_db)

    response = client.post(
        "/api/missions/es-beta/submit",
        json={"completion_data": "COMPLETE es-beta"},
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}
