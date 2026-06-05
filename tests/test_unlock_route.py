"""Tests for GET /unlock/<token> and OAuth-staged unlock redemption."""

from pathlib import Path

import pytest

from radspion.web.session_keys import (
    SESSION_PENDING_UNLOCK,
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


def test_unlock_link_stages_pending_code(storyline_db: Path):
    client, _oauth = _client_for_db(storyline_db)
    response = client.get("/unlock/EXAMPLE-UNLOCK")

    assert response.status_code == 200
    assert b"Mission unlock" in response.data
    assert b"Apply mission unlock" not in response.data
    assert b"Sign in with Google" in response.data
    with client.session_transaction() as sess:
        assert sess[SESSION_PENDING_UNLOCK] == "EXAMPLE-UNLOCK"


def test_unlock_link_invalid_token_redirects_home(storyline_db: Path):
    client, _oauth = _client_for_db(storyline_db)
    response = client.get("/unlock/%20%20")

    assert response.status_code == 302
    assert response.location.endswith("/")
    with client.session_transaction() as sess:
        assert SESSION_PENDING_UNLOCK not in sess


def test_unlock_signed_in_shows_confirm_form(storyline_db: Path):
    client, _oauth = _client_for_db(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = diana_id

    response = client.get("/unlock/HIDDEN-UNLOCK")

    assert response.status_code == 200
    assert b"Apply mission unlock" in response.data
    assert b"Sign in with Google" not in response.data
    assert b'value="HIDDEN-UNLOCK"' in response.data


def test_unlock_signed_in_redeem_via_api(storyline_db: Path):
    client, _oauth = _client_for_db(storyline_db)
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = diana_id

    client.get("/unlock/EXAMPLE-UNLOCK")
    unlock = client.post("/api/unlock", json={"unlock_code": "EXAMPLE-UNLOCK"})

    assert unlock.status_code == 200
    assert unlock.get_json()["outcome"] == "success"
    assert len(unlock.get_json()["new_missions"]) == 2


def test_oauth_returning_user_redeems_pending_unlock(storyline_db: Path):
    oauth = FakeGoogleOAuth()
    client, _ = _client_for_db(storyline_db, oauth=oauth)
    diana = SAMPLE_AGENTS["diana"]

    client.get("/unlock/EXAMPLE-UNLOCK")
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
    assert b"RADSPION_POST_LOGIN_UNLOCK" in dashboard.data
    assert b'"outcome": "success"' in dashboard.data or b'"outcome":"success"' in dashboard.data
    assert b"es-alpha" in dashboard.data
    assert b"es-beta" in dashboard.data
    with client.session_transaction() as sess:
        assert SESSION_PENDING_UNLOCK not in sess

    second_load = client.get("/agent/dashboard")
    assert b"RADSPION_POST_LOGIN_UNLOCK" not in second_load.data


def test_second_login_without_unlock_link_skips_modal(storyline_db: Path):
    oauth = FakeGoogleOAuth()
    client, _ = _client_for_db(storyline_db, oauth=oauth)
    diana = SAMPLE_AGENTS["diana"]

    client.get("/unlock/EXAMPLE-UNLOCK")
    client.get("/auth/google")
    oauth.returns(
        google_subject_id=diana["google_subject_id"],
        email=diana["email"],
        display_name=diana["display_name"],
    )
    complete_oauth_callback(client, oauth)
    first_dashboard = client.get("/agent/dashboard")
    assert b"RADSPION_POST_LOGIN_UNLOCK" in first_dashboard.data

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
    assert b"RADSPION_POST_LOGIN_UNLOCK" not in second_dashboard.data


def test_oauth_new_user_redeems_unlock_without_access_gate(storyline_db: Path):
    oauth = FakeGoogleOAuth()
    client, _ = _client_for_db(storyline_db, oauth=oauth)

    client.get("/unlock/HIDDEN-UNLOCK")
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
    assert b"RADSPION_POST_LOGIN_UNLOCK" in dashboard.data
    assert b"es-hidden" in dashboard.data
    with client.session_transaction() as sess:
        assert SESSION_PENDING_UNLOCK not in sess
