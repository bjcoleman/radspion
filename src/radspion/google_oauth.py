"""Google OAuth for server-side redirect flow."""

from typing import Any

from google.auth import exceptions as google_auth_exceptions
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from oauthlib.oauth2.rfc6749 import errors as oauth2_errors

from radspion.oauth_types import (
    GoogleProfile,
    OAuthCodeError,
    OAuthStateError,
    OAuthVerificationError,
)
from radspion.web.session_keys import SESSION_PENDING_SUBMIT_DATA

SESSION_OAUTH_STATE = "oauth_state"
SESSION_OAUTH_CODE_VERIFIER = "oauth_code_verifier"

_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


class GoogleOAuth:
    """Start and complete Google OAuth using google-auth-oauthlib."""

    def __init__(
        self,
        *,
        base_url: str,
        google_client_id: str,
        google_client_secret: str,
    ) -> None:
        self._redirect_uri = f"{base_url.rstrip('/')}/auth/google/callback"
        self._google_client_id = google_client_id
        self._client_config = {
            "web": {
                "client_id": google_client_id,
                "client_secret": google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self._redirect_uri],
            }
        }
        # Keyed by OAuth state from the callback URL so PKCE survives
        # the cross-site redirect when the browser omits the session cookie.
        self._pending_by_state: dict[str, dict[str, Any]] = {}

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    def _create_flow(self) -> Flow:
        return Flow.from_client_config(
            self._client_config,
            scopes=_SCOPES,
            redirect_uri=self._redirect_uri,
        )

    def authorization_url(self, session) -> str:
        """Store OAuth state and return the Google authorization URL."""
        flow = self._create_flow()
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
        )
        self._pending_by_state[state] = {
            "code_verifier": flow.code_verifier,
            # Move out of the browser session so a stale QR visit cannot re-submit
            # on every later Sign in with Google from the landing page.
            "pending_submit_data": session.pop(SESSION_PENDING_SUBMIT_DATA, None),
        }
        session[SESSION_OAUTH_STATE] = state
        if flow.code_verifier:
            session[SESSION_OAUTH_CODE_VERIFIER] = flow.code_verifier
        if hasattr(session, "modified"):
            session.modified = True
        return authorization_url

    def _restore_pending_session_flags(self, session, pending: dict[str, Any]) -> None:
        pending_data = pending.get("pending_submit_data")
        if pending_data:
            session[SESSION_PENDING_SUBMIT_DATA] = pending_data

    def _resolve_callback_context(self, session, *, state: str | None) -> str | None:
        """Return the PKCE verifier for callback validation."""
        if state:
            pending = self._pending_by_state.pop(state, None)
            if pending is not None:
                self._restore_pending_session_flags(session, pending)
                return pending["code_verifier"]

        expected_state = session.pop(SESSION_OAUTH_STATE, None)
        if not expected_state or state != expected_state:
            session.pop(SESSION_OAUTH_CODE_VERIFIER, None)
            raise OAuthStateError("Invalid OAuth state")

        code_verifier = session.pop(SESSION_OAUTH_CODE_VERIFIER, None)
        return code_verifier

    def profile_from_callback(self, session, *, code: str, state: str | None) -> GoogleProfile:
        """Exchange the authorization code and return verified profile fields."""
        if not code:
            raise OAuthCodeError("Missing authorization code")
        if not state:
            raise OAuthStateError("Missing OAuth state")

        code_verifier = self._resolve_callback_context(session, state=state)
        flow = self._create_flow()
        if code_verifier:
            flow.code_verifier = code_verifier
        flow.oauth2session.state = state

        try:
            flow.fetch_token(code=code)
        except oauth2_errors.OAuth2Error as exc:
            raise OAuthCodeError(str(exc)) from exc
        except ValueError as exc:
            raise OAuthCodeError(str(exc)) from exc

        credentials = flow.credentials
        request_obj = google_requests.Request()
        try:
            id_info = id_token.verify_oauth2_token(
                credentials.id_token,
                request_obj,
                self._google_client_id,
            )
        except (ValueError, google_auth_exceptions.GoogleAuthError) as exc:
            raise OAuthVerificationError(str(exc)) from exc

        sub = id_info.get("sub")
        email = id_info.get("email")
        name = id_info.get("name")
        if not sub or not email or not name:
            raise OAuthVerificationError("Token missing required fields")

        return GoogleProfile(
            google_subject_id=sub,
            email=email,
            display_name=name,
        )
