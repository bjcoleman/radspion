"""Tests for GET /link/<token> and OAuth-staged data submission."""

from pathlib import Path

import pytest

from radspion.web.session_keys import (
    SESSION_PENDING_SUBMIT_DATA,
    SESSION_USER_ID,
)
from tests.conftest import complete_oauth_callback
from tests.fakes.google_oauth import FakeGoogleOAuth
from tests.helpers import SAMPLE_AGENTS, load_testing_storyline_database


@pytest.fixture
def storyline_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "storyline.db"
    load_testing_storyline_database(db_path)
    return db_path


def _client_for_db(db_path: Path, *, oauth: FakeGoogleOAuth | None = None):
    from radspion.app import create_app
    from radspion.config import load_config
    from radspion.database import DatabaseRadspionStorage
    from radspion.radspion import Radspion

    config = load_config(testing=True)
    radspion = Radspion(DatabaseRadspionStorage(db_path))
    if oauth is None:
        oauth = FakeGoogleOAuth()
    return create_app(config=config, radspion=radspion, oauth=oauth).test_client(), oauth


def test_link_stages_pending_data(storyline_db: Path):
    client, _oauth = _client_for_db(storyline_db)
    response = client.get("/link/EXAMPLE%20UNLOCK")

    assert response.status_code == 200
    assert b"Secure data link" in response.data
    assert b"link-form__submit" not in response.data
    assert b"Sign in with Google" in response.data
    with client.session_transaction() as sess:
        assert sess[SESSION_PENDING_SUBMIT_DATA] == "EXAMPLE UNLOCK"


def test_link_invalid_token_redirects_home(storyline_db: Path):
    client, _oauth = _client_for_db(storyline_db)
    response = client.get("/link/%20%20")

    assert response.status_code == 302
    assert response.location.endswith("/")
    with client.session_transaction() as sess:
        assert SESSION_PENDING_SUBMIT_DATA not in sess


def test_link_signed_in_shows_confirm_form(storyline_db: Path):
    client, _oauth = _client_for_db(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = diana_id

    response = client.get("/link/HIDDEN%20UNLOCK")

    assert response.status_code == 200
    assert b"Submit data" in response.data
    assert b"Sign in with Google" not in response.data
    assert b'value="HIDDEN UNLOCK"' in response.data
    assert b'name="data"' in response.data


def test_link_signed_in_submits_via_api(storyline_db: Path):
    client, _oauth = _client_for_db(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = diana_id

    client.get("/link/EXAMPLE%20UNLOCK")
    submit = client.post("/api/submit", json={"data": "EXAMPLE UNLOCK"})

    assert submit.status_code == 200
    assert submit.get_json()["outcome"] == "success"
    assert len(submit.get_json()["new_missions"]) == 2


def test_oauth_returning_user_submits_pending_data(storyline_db: Path):
    oauth = FakeGoogleOAuth()
    client, _ = _client_for_db(storyline_db, oauth=oauth)
    diana = SAMPLE_AGENTS["diana"]

    client.get("/link/EXAMPLE%20UNLOCK")
    client.get("/auth/google")
    oauth.returns(
        google_subject_id=diana["google_subject_id"],
        email=diana["email"],
        display_name=diana["display_name"],
    )

    response = complete_oauth_callback(client, oauth)

    assert response.status_code == 302
    assert response.location.endswith("/agent/dashboard")
    dashboard = client.get("/agent/dashboard")
    assert b"RADSPION_STAGED_SUBMIT_RESULT" in dashboard.data
    assert b'"outcome": "success"' in dashboard.data or b'"outcome":"success"' in dashboard.data
    assert b"es-alpha" in dashboard.data
    assert b"es-beta" in dashboard.data
    with client.session_transaction() as sess:
        assert SESSION_PENDING_SUBMIT_DATA not in sess

    second_load = client.get("/agent/dashboard")
    assert b"RADSPION_STAGED_SUBMIT_RESULT" not in second_load.data


def test_second_login_without_link_skips_modal(storyline_db: Path):
    oauth = FakeGoogleOAuth()
    client, _ = _client_for_db(storyline_db, oauth=oauth)
    diana = SAMPLE_AGENTS["diana"]

    client.get("/link/EXAMPLE%20UNLOCK")
    client.get("/auth/google")
    oauth.returns(
        google_subject_id=diana["google_subject_id"],
        email=diana["email"],
        display_name=diana["display_name"],
    )
    complete_oauth_callback(client, oauth)
    first_dashboard = client.get("/agent/dashboard")
    assert b"RADSPION_STAGED_SUBMIT_RESULT" in first_dashboard.data

    with client.session_transaction() as sess:
        sess.clear()
        sess[SESSION_USER_ID] = diana["id"]

    client.get("/auth/google")
    oauth.returns(
        google_subject_id=diana["google_subject_id"],
        email=diana["email"],
        display_name=diana["display_name"],
    )
    complete_oauth_callback(client, oauth)
    second_dashboard = client.get("/agent/dashboard")
    assert b"RADSPION_STAGED_SUBMIT_RESULT" not in second_dashboard.data


def test_oauth_new_user_submits_data_without_access_gate(storyline_db: Path):
    oauth = FakeGoogleOAuth()
    client, _ = _client_for_db(storyline_db, oauth=oauth)

    client.get("/link/HIDDEN%20UNLOCK")
    client.get("/auth/google")
    oauth.returns(
        google_subject_id="google-new",
        email="new@example.com",
        display_name="New Agent",
    )

    response = complete_oauth_callback(client, oauth)

    assert response.status_code == 302
    assert response.location.endswith("/agent/dashboard")
    dashboard = client.get("/agent/dashboard")
    assert b"RADSPION_STAGED_SUBMIT_RESULT" in dashboard.data
    assert b"es-hidden" in dashboard.data
    with client.session_transaction() as sess:
        assert SESSION_PENDING_SUBMIT_DATA not in sess


def test_legacy_unlock_route_removed(storyline_db: Path):
    client, _oauth = _client_for_db(storyline_db)
    assert client.get("/unlock/EXAMPLE%20UNLOCK").status_code == 404
