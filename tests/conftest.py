"""Shared pytest fixtures."""

import pytest

from radspion.app import create_app
from radspion.config import load_config
from radspion.radspion import Radspion
from radspion.user import User
from tests.fakes.google_oauth import FakeGoogleOAuth
from tests.fakes.storage import InMemoryRadspionStorage


@pytest.fixture
def config():
    return load_config(testing=True)


@pytest.fixture
def storage():
    """In-memory storage for auth and route tests."""
    return InMemoryRadspionStorage()


@pytest.fixture
def radspion(storage):
    return Radspion(storage)


@pytest.fixture
def oauth():
    return FakeGoogleOAuth()


@pytest.fixture
def app(config, radspion, oauth):
    return create_app(config=config, radspion=radspion, oauth=oauth)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def existing_user(storage):
    """Alice-like user already in storage."""
    user = User(
        id=1,
        email="alice@example.com",
        google_subject_id="google-alice",
        display_name="Alice",
        codename="Alice",
    )
    storage._users[user.id] = user
    storage._next_user_id = 2
    return user


def complete_oauth_callback(client, oauth, *, code="test-code", state="test-oauth-state"):
    """Drive the OAuth callback with a configured fake."""
    with client.session_transaction() as sess:
        sess["oauth_state"] = state
        sess["oauth_code_verifier"] = "test-verifier"
    return client.get(f"/auth/google/callback?code={code}&state={state}")
