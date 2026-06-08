"""Tests for POST /api/codename."""

from pathlib import Path

import pytest

from radspion.codename import (
    DUPLICATE_CODENAME_MESSAGE,
    INVALID_LENGTH_MESSAGE,
    SUCCESS_MESSAGE,
)
from radspion.database import DatabaseRadspionStorage
from radspion.web.api import MISSING_CODENAME_ERROR
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
    from radspion.radspion import Radspion
    from tests.fakes.google_oauth import FakeGoogleOAuth

    config = load_config(testing=True)
    radspion = Radspion(DatabaseRadspionStorage(db_path))
    return create_app(config=config, radspion=radspion, oauth=FakeGoogleOAuth()).test_client()


def test_codename_success_updates_user(storyline_db: Path):
    client = _client_for_db(storyline_db)
    diana = SAMPLE_AGENTS["diana"]
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = diana["id"]

    response = client.post("/api/codename", json={"codename": "  Night-Owl  "})
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"outcome": "success", "message": SUCCESS_MESSAGE}

    storage = DatabaseRadspionStorage(storyline_db)
    user = storage.find_user_by_id(diana["id"])
    assert user is not None
    assert user.codename == "Night-Owl"


def test_codename_same_value_is_success(storyline_db: Path):
    client = _client_for_db(storyline_db)
    diana = SAMPLE_AGENTS["diana"]
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = diana["id"]

    response = client.post("/api/codename", json={"codename": diana["codename"]})
    assert response.status_code == 200
    assert response.get_json() == {"outcome": "success", "message": SUCCESS_MESSAGE}


def test_codename_duplicate_returns_message(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/codename", json={"codename": SAMPLE_AGENTS["alice"]["codename"]})
    assert response.status_code == 200
    assert response.get_json() == {
        "outcome": "invalid",
        "message": DUPLICATE_CODENAME_MESSAGE,
    }


def test_codename_duplicate_is_case_sensitive(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/codename", json={"codename": "alice"})
    assert response.status_code == 200
    assert response.get_json()["outcome"] == "success"


def test_codename_invalid_length_returns_message(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/codename", json={"codename": "abc"})
    assert response.status_code == 200
    assert response.get_json() == {
        "outcome": "invalid",
        "message": INVALID_LENGTH_MESSAGE,
    }


def test_codename_rejects_missing_body(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/codename", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": MISSING_CODENAME_ERROR}


def test_codename_rejects_empty_codename(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post("/api/codename", json={"codename": "   "})
    assert response.status_code == 400


def test_codename_rejects_non_json_body(storyline_db: Path):
    client = _client_for_db(storyline_db)
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = client.post(
        "/api/codename",
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": MISSING_CODENAME_ERROR}


def test_codename_requires_sign_in(storyline_db: Path):
    client = _client_for_db(storyline_db)

    response = client.post("/api/codename", json={"codename": "Night-Owl"})
    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}
