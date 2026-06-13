"""Tests for GET /clearance/<token> and OAuth-staged clearance redemption."""

from radspion.app import create_app
from radspion.config import load_config
from radspion.database import DatabaseRadspionStorage
from radspion.radspion import Radspion
from radspion.web.session_keys import (
    SESSION_PENDING_CLEARANCE,
    SESSION_USER_ID,
)
from tests.conftest import complete_oauth_callback
from tests.fakes.google_oauth import FakeGoogleOAuth
from tests.helpers import SAMPLE_AGENTS


def _oauth_client(testing_storyline_storage: DatabaseRadspionStorage, oauth: FakeGoogleOAuth):
    config = load_config(testing=True)
    radspion = Radspion(testing_storyline_storage)
    return create_app(config=config, radspion=radspion, oauth=oauth).test_client()


def test_clearance_link_stages_pending_code(testing_storyline_oauth_client):
    client, _oauth = testing_storyline_oauth_client
    response = client.get("/clearance/EXAMPLE-CLEARANCE")

    assert response.status_code == 200
    assert b"Clearance request" in response.data
    assert b"Request Access" not in response.data
    assert b"Sign in with Google" in response.data
    with client.session_transaction() as sess:
        assert sess[SESSION_PENDING_CLEARANCE] == "EXAMPLE-CLEARANCE"


def test_clearance_link_invalid_token_redirects_home(testing_storyline_oauth_client):
    client, _oauth = testing_storyline_oauth_client
    response = client.get("/clearance/%20%20")

    assert response.status_code == 302
    assert response.location.endswith("/")
    with client.session_transaction() as sess:
        assert SESSION_PENDING_CLEARANCE not in sess


def test_clearance_signed_in_shows_confirm_form(testing_storyline_oauth_client):
    client, _oauth = testing_storyline_oauth_client
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = diana_id

    response = client.get("/clearance/HIDDEN-CLEARANCE")

    assert response.status_code == 200
    assert b"Request Access" in response.data
    assert b"Sign in with Google" not in response.data
    assert b'value="HIDDEN-CLEARANCE"' in response.data


def test_clearance_signed_in_redeem_via_api(testing_storyline_oauth_client):
    client, _oauth = testing_storyline_oauth_client
    diana_id = SAMPLE_AGENTS["diana"]["id"]

    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = diana_id

    client.get("/clearance/EXAMPLE-CLEARANCE")
    clearance = client.post("/api/clearance", json={"clearance_code": "EXAMPLE-CLEARANCE"})

    assert clearance.status_code == 200
    assert clearance.get_json()["outcome"] == "success"
    assert len(clearance.get_json()["new_missions"]) == 2


def test_oauth_returning_user_redeems_pending_clearance(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    oauth = FakeGoogleOAuth()
    client = _oauth_client(testing_storyline_storage, oauth)
    diana = SAMPLE_AGENTS["diana"]

    client.get("/clearance/EXAMPLE-CLEARANCE")
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
    assert b"RADSPION_POST_LOGIN_CLEARANCE" in dashboard.data
    assert b'"outcome": "success"' in dashboard.data or b'"outcome":"success"' in dashboard.data
    assert b"es-alpha" in dashboard.data
    assert b"es-beta" in dashboard.data
    with client.session_transaction() as sess:
        assert SESSION_PENDING_CLEARANCE not in sess

    second_load = client.get("/agent/dashboard")
    assert b"RADSPION_POST_LOGIN_CLEARANCE" not in second_load.data


def test_second_login_without_clearance_link_skips_modal(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    oauth = FakeGoogleOAuth()
    client = _oauth_client(testing_storyline_storage, oauth)
    diana = SAMPLE_AGENTS["diana"]

    client.get("/clearance/EXAMPLE-CLEARANCE")
    client.get("/auth/google")
    oauth.returns(
        google_subject_id=diana["google_subject_id"],
        email=diana["email"],
        display_name=diana["display_name"],
    )
    complete_oauth_callback(client, oauth)
    first_dashboard = client.get("/agent/dashboard")
    assert b"RADSPION_POST_LOGIN_CLEARANCE" in first_dashboard.data

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
    assert b"RADSPION_POST_LOGIN_CLEARANCE" not in second_dashboard.data


def test_oauth_new_user_redeems_clearance_without_access_gate(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    oauth = FakeGoogleOAuth()
    client = _oauth_client(testing_storyline_storage, oauth)

    client.get("/clearance/HIDDEN-CLEARANCE")
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
    assert b"RADSPION_POST_LOGIN_CLEARANCE" in dashboard.data
    assert b"es-hidden" in dashboard.data
    with client.session_transaction() as sess:
        assert SESSION_PENDING_CLEARANCE not in sess
