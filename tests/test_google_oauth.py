"""Tests for GoogleOAuth configuration."""

from unittest.mock import MagicMock, patch

import pytest

from radspion.google_oauth import SESSION_OAUTH_CODE_VERIFIER, SESSION_OAUTH_STATE, GoogleOAuth
from radspion.oauth_types import OAuthCodeError, OAuthStateError
from radspion.web.session_keys import SESSION_REGISTRATION_CLEARED


def test_redirect_uri_uses_callback_path():
    oauth = GoogleOAuth(
        base_url="http://localhost:8000",
        google_client_id="client-id",
        google_client_secret="client-secret",
    )

    assert oauth.redirect_uri == "http://localhost:8000/auth/google/callback"


def test_authorization_url_stores_pending_and_session_state():
    oauth = GoogleOAuth(
        base_url="http://localhost:8000",
        google_client_id="client-id",
        google_client_secret="client-secret",
    )
    session = {}

    with patch("radspion.google_oauth.Flow") as flow_class:
        flow = MagicMock()
        flow.authorization_url.return_value = ("https://accounts.google.com/auth", "state-abc")
        flow.code_verifier = "verifier-xyz"
        flow_class.from_client_config.return_value = flow

        url = oauth.authorization_url(session)

    assert url == "https://accounts.google.com/auth"
    assert session[SESSION_OAUTH_STATE] == "state-abc"
    assert session[SESSION_OAUTH_CODE_VERIFIER] == "verifier-xyz"
    assert oauth._pending_by_state["state-abc"]["code_verifier"] == "verifier-xyz"


def test_profile_from_callback_uses_pending_when_session_empty():
    oauth = GoogleOAuth(
        base_url="http://localhost:8000",
        google_client_id="client-id",
        google_client_secret="client-secret",
    )
    oauth._pending_by_state["state-abc"] = {
        "code_verifier": "verifier-xyz",
        "registration_cleared": True,
    }
    session = {}

    with (
        patch("radspion.google_oauth.id_token.verify_oauth2_token") as mock_verify,
        patch("radspion.google_oauth.Flow") as mock_flow_class,
    ):
        flow = MagicMock()
        flow.credentials.id_token = "id-token"
        mock_flow_class.from_client_config.return_value = flow
        mock_verify.return_value = {
            "sub": "google-sub",
            "email": "user@example.com",
            "name": "Test User",
        }

        profile = oauth.profile_from_callback(session, code="auth-code", state="state-abc")

    assert profile.email == "user@example.com"
    assert session[SESSION_REGISTRATION_CLEARED] is True
    assert "state-abc" not in oauth._pending_by_state


def test_profile_from_callback_rejects_missing_state():
    oauth = GoogleOAuth(
        base_url="http://localhost:8000",
        google_client_id="client-id",
        google_client_secret="client-secret",
    )

    with pytest.raises(OAuthStateError):
        oauth.profile_from_callback({}, code="auth-code", state=None)


def test_profile_from_callback_rejects_missing_code():
    oauth = GoogleOAuth(
        base_url="http://localhost:8000",
        google_client_id="client-id",
        google_client_secret="client-secret",
    )

    with pytest.raises(OAuthCodeError):
        oauth.profile_from_callback({}, code="", state="state-abc")


def test_profile_from_callback_rejects_state_mismatch():
    oauth = GoogleOAuth(
        base_url="http://localhost:8000",
        google_client_id="client-id",
        google_client_secret="client-secret",
    )
    session = {SESSION_OAUTH_STATE: "expected-state"}

    with pytest.raises(OAuthStateError):
        oauth.profile_from_callback(session, code="auth-code", state="wrong-state")


@patch("radspion.google_oauth.id_token.verify_oauth2_token")
@patch("radspion.google_oauth.Flow")
def test_profile_from_callback_returns_profile(mock_flow_class, mock_verify):
    oauth = GoogleOAuth(
        base_url="http://localhost:8000",
        google_client_id="client-id",
        google_client_secret="client-secret",
    )
    session = {
        SESSION_OAUTH_STATE: "state-abc",
        SESSION_OAUTH_CODE_VERIFIER: "verifier-xyz",
    }

    flow = MagicMock()
    flow.credentials.id_token = "id-token"
    mock_flow_class.from_client_config.return_value = flow
    mock_verify.return_value = {
        "sub": "google-sub",
        "email": "user@example.com",
        "name": "Test User",
    }

    profile = oauth.profile_from_callback(session, code="auth-code", state="state-abc")

    assert profile.google_subject_id == "google-sub"
    assert profile.email == "user@example.com"
    assert profile.display_name == "Test User"
    flow.fetch_token.assert_called_once_with(code="auth-code")
