"""Fake Google OAuth for tests."""

from radspion.google_oauth import SESSION_OAUTH_CODE_VERIFIER, SESSION_OAUTH_STATE
from radspion.oauth_types import (
    GoogleProfile,
    OAuthCodeError,
    OAuthStateError,
)
from radspion.web.session_keys import SESSION_PENDING_CLEARANCE


class FakeGoogleOAuth:
    """Configurable OAuth double; no network calls."""

    def __init__(self) -> None:
        self._profile: GoogleProfile | None = None
        self._exception: Exception | None = None
        self._pending_by_state: dict[str, dict] = {}
        self.redirect_uri = "http://localhost:8000/auth/google/callback"

    def returns(self, *, google_subject_id: str, email: str, display_name: str) -> None:
        """Configure a successful callback."""
        self._profile = GoogleProfile(
            google_subject_id=google_subject_id,
            email=email,
            display_name=display_name,
        )
        self._exception = None

    def raises(self, exception: Exception) -> None:
        """Configure callback failure."""
        self._exception = exception
        self._profile = None

    def authorization_url(self, session) -> str:
        state = "test-oauth-state"
        session[SESSION_OAUTH_STATE] = state
        session[SESSION_OAUTH_CODE_VERIFIER] = "test-verifier"
        self._pending_by_state[state] = {
            "pending_clearance": session.pop(SESSION_PENDING_CLEARANCE, None),
        }
        return "https://accounts.google.test/o/oauth2/auth"

    def profile_from_callback(self, session, *, code: str, state: str | None) -> GoogleProfile:
        if self._exception is not None:
            raise self._exception

        pending = self._pending_by_state.pop(state, None)
        if pending is not None:
            pending_clearance = pending.get("pending_clearance")
            if pending_clearance:
                session[SESSION_PENDING_CLEARANCE] = pending_clearance

        expected_state = session.pop(SESSION_OAUTH_STATE, None)
        session.pop(SESSION_OAUTH_CODE_VERIFIER, None)
        if state != expected_state:
            raise OAuthStateError("Invalid OAuth state")

        if not code:
            raise OAuthCodeError("Missing authorization code")

        if self._profile is None:
            return GoogleProfile(
                google_subject_id="google-default",
                email="default@example.com",
                display_name="Default User",
            )
        return self._profile
