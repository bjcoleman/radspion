"""Authentication helpers for acceptance tests."""

from __future__ import annotations

from playwright.sync_api import Page, expect

_OAUTH_CALLBACK_CODE = "test-code"
_OAUTH_CALLBACK_STATE = "test-oauth-state"


def expect_landing_requires_sign_in(page: Page) -> None:
    expect(page.get_by_text("Sign in to continue")).to_be_visible()


def perform_fake_oauth(login_as, agent_key: str) -> None:
    """Sign in via fake OAuth (uses the browser page's shared cookie jar)."""
    login_as(agent_key)


def sign_in_oauth_user(
    page: Page,
    live_app,
    *,
    google_subject_id: str,
    email: str,
    display_name: str,
) -> None:
    """Sign in as a user not in the Testing Storyline cast (provisions on first sign-in)."""
    live_app.oauth.returns(
        google_subject_id=google_subject_id,
        email=email,
        display_name=display_name,
    )
    page.request.get(f"{live_app.base_url}/auth/google", max_redirects=0)
    page.request.get(
        f"{live_app.base_url}/auth/google/callback"
        f"?code={_OAUTH_CALLBACK_CODE}&state={_OAUTH_CALLBACK_STATE}",
        max_redirects=0,
    )
