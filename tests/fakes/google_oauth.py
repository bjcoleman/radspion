"""Fake Google OAuth for tests."""

from radspion.google_oauth import SESSION_OAUTH_CODE_VERIFIER, SESSION_OAUTH_STATE
from radspion.oauth_types import (
    GoogleProfile,
    OAuthCodeError,
    OAuthStateError,
)


class FakeGoogleOAuth:
    """Configurable OAuth double; no network calls."""

    def __init__(self) -> None:
        self._profile: GoogleProfile | None = None
        self._exception: Exception | None = None
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
        session[SESSION_OAUTH_STATE] = "test-oauth-state"
        session[SESSION_OAUTH_CODE_VERIFIER] = "test-verifier"
        return "https://accounts.google.test/o/oauth2/auth"

    def profile_from_callback(self, session, *, code: str, state: str | None) -> GoogleProfile:
        if self._exception is not None:
            raise self._exception

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
