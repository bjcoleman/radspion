"""OAuth profile data returned after Google sign-in."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GoogleProfile:
    """Verified Google account fields used for sign-in or provisioning."""

    google_subject_id: str
    email: str
    display_name: str


class OAuthError(Exception):
    """Base class for OAuth failures."""


class OAuthStateError(OAuthError):
    """OAuth state did not match the value stored in the session."""


class OAuthCodeError(OAuthError):
    """Authorization code was missing, invalid, or expired."""


class OAuthVerificationError(OAuthError):
    """ID token verification failed."""
