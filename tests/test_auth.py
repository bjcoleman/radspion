"""Tests for OAuth routes and login guards."""

from radspion.app import create_app
from radspion.config import load_config
from radspion.oauth_types import OAuthCodeError, OAuthStateError, OAuthVerificationError
from radspion.radspion import Radspion
from radspion.web.session_keys import SESSION_USER_ID
from tests.conftest import complete_oauth_callback
from tests.fakes.storage import InMemoryRadspionStorage


def test_google_login_redirects_to_authorization_url(client):
    response = client.get("/auth/google")
    assert response.status_code == 302
    assert response.location == "https://accounts.google.test/o/oauth2/auth"


def test_oauth_callback_signs_in_existing_user(client, oauth, existing_user):
    oauth.returns(
        google_subject_id=existing_user.google_subject_id,
        email=existing_user.email,
        display_name=existing_user.display_name,
    )

    response = complete_oauth_callback(client, oauth)

    assert response.status_code == 302
    assert response.location.endswith("/agent/dashboard")
    with client.session_transaction() as sess:
        assert sess[SESSION_USER_ID] == existing_user.id


def test_oauth_callback_provisions_new_user(oauth):
    storage = InMemoryRadspionStorage()
    config = load_config(testing=True)
    client = create_app(
        config=config,
        radspion=Radspion(storage),
        oauth=oauth,
    ).test_client()
    oauth.returns(
        google_subject_id="google-new",
        email="new@example.com",
        display_name="New Agent",
    )

    response = complete_oauth_callback(client, oauth)

    assert response.status_code == 302
    with client.session_transaction() as sess:
        user_id = sess[SESSION_USER_ID]
    user = storage.find_user_by_id(user_id)
    assert user is not None
    assert user.email == "new@example.com"


def test_oauth_callback_handles_invalid_code(client, oauth):
    oauth.raises(OAuthCodeError("bad code"))

    response = complete_oauth_callback(client, oauth)

    assert response.status_code == 302
    assert "Sign-in was cancelled" in client.get("/").data.decode()


def test_oauth_callback_handles_state_error(client, oauth):
    oauth.raises(OAuthStateError("bad state"))

    response = complete_oauth_callback(client, oauth)

    assert response.status_code == 302
    assert "could not be verified" in client.get("/").data.decode()


def test_oauth_callback_handles_verification_error(client, oauth):
    oauth.raises(OAuthVerificationError("bad token"))

    response = complete_oauth_callback(client, oauth)

    assert response.status_code == 302
    assert "could not be verified" in client.get("/").data.decode()


def test_dashboard_requires_login(client):
    response = client.get("/agent/dashboard")
    assert response.status_code == 302
    assert response.location.endswith("/")
    assert "Sign in to continue" in client.get("/").data.decode()


def test_dashboard_shows_user_when_logged_in(client, existing_user):
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = existing_user.id

    response = client.get("/agent/dashboard")
    assert response.status_code == 200
    assert "Alice" in response.data.decode()


def test_logout_clears_session(client, existing_user):
    with client.session_transaction() as sess:
        sess[SESSION_USER_ID] = existing_user.id

    response = client.post("/auth/logout")

    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert SESSION_USER_ID not in sess
    assert "signed out" in client.get("/").data.decode()
