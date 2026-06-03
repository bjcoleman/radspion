"""Tests for POST /api/submit."""

from pathlib import Path

import pytest

from radspion.web.api import INVALID_DATA_MESSAGE
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


def test_submit_data_unlock_success(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/submit", json={"data": "EXAMPLE UNLOCK"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "success"
    assert data["kind"] == "unlock"
    slugs = {mission["slug"] for mission in data["new_missions"]}
    assert slugs == {"es-alpha", "es-beta"}
    assert data["new_missions"][0]["group_name"] == "Testing Storyline"
    assert "mission_slug" not in data


def test_submit_data_unlock_invalid(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/submit", json={"data": "ZZ-INVALID"})
    assert response.status_code == 200
    assert response.get_json() == {"outcome": "invalid", "message": INVALID_DATA_MESSAGE}


def test_submit_data_unlock_already_done(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.post("/api/submit", json={"data": "EXAMPLE UNLOCK"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "already_done"
    assert data["new_missions"] == []
    assert "message" in data
    assert "kind" not in data


def test_submit_data_complete_success(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.post("/api/submit", json={"data": "COMPLETE es-beta"})
    assert response.status_code == 200
    data = response.get_json()
    assert data == {
        "outcome": "success",
        "new_missions": [],
        "kind": "complete",
        "mission_slug": "es-beta",
    }


def test_submit_data_complete_success_with_new_missions(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["charlie"]["id"]

    response = client.post("/api/submit", json={"data": "COMPLETE es-alpha"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "success"
    assert data["kind"] == "complete"
    assert data["mission_slug"] == "es-alpha"
    assert len(data["new_missions"]) == 1
    assert data["new_missions"][0]["slug"] == "es-gamma"


def test_submit_data_complete_invalid(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = client.post("/api/submit", json={"data": "WRONG"})
    assert response.status_code == 200
    assert response.get_json() == {"outcome": "invalid", "message": INVALID_DATA_MESSAGE}


def test_submit_data_complete_invalid_when_not_listed(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/submit", json={"data": "COMPLETE es-alpha"})
    assert response.status_code == 200
    assert response.get_json() == {"outcome": "invalid", "message": INVALID_DATA_MESSAGE}


def test_submit_data_complete_already_done(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["bob"]["id"]

    response = client.post("/api/submit", json={"data": "COMPLETE es-alpha"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "already_done"
    assert data["new_missions"] == []
    assert "message" in data


def test_submit_data_rejects_missing_data(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/submit", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing data"}


def test_submit_data_rejects_empty_data(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/submit", json={"data": "   "})
    assert response.status_code == 400


def test_submit_data_rejects_non_json_body(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post(
        "/api/submit",
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing data"}


def test_submit_data_requires_sign_in(storyline_db: Path):
    client = _client_for_db(storyline_db)

    response = client.post("/api/submit", json={"data": "EXAMPLE UNLOCK"})
    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}


def test_legacy_api_routes_removed(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    assert client.post("/api/unlock", json={"unlock_code": "x"}).status_code == 404
    assert (
        client.post(
            "/api/missions/es-beta/submit",
            json={"completion_code": "x"},
        ).status_code
        == 404
    )


def test_submit_success_stages_session_for_modal(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/submit", json={"data": "EXAMPLE UNLOCK"})
    assert response.status_code == 200

    with client.session_transaction() as sess:
        assert sess.get("staged_submit_result", {}).get("outcome") == "success"

    dashboard = client.get("/agent/dashboard")
    body = dashboard.data.decode()
    assert "RADSPION_STAGED_SUBMIT_RESULT" in body
    assert body.index("RADSPION_STAGED_SUBMIT_RESULT") < body.index("submit-result.js")

    second = client.get("/agent/dashboard")
    assert b"RADSPION_STAGED_SUBMIT_RESULT" not in second.data
