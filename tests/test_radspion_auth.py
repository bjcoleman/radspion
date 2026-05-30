"""Tests for Radspion sign-in and provisioning."""

import pytest

from radspion.oauth_types import GoogleProfile, SignupNotAllowedError
from radspion.radspion import Radspion
from tests.fakes.storage import ORIENTATION_GROUP_ID, InMemoryRadspionStorage


def _profile(**overrides):
    defaults = {
        "google_subject_id": "google-new",
        "email": "new@example.com",
        "display_name": "New Agent",
    }
    defaults.update(overrides)
    return GoogleProfile(**defaults)


def test_sign_in_returns_existing_user_by_google_subject_id():
    storage = InMemoryRadspionStorage()
    existing = storage.create_user(
        email="alice@example.com",
        google_subject_id="google-alice",
        display_name="Alice",
    )
    app = Radspion(storage)

    user = app.sign_in_with_google(
        _profile(google_subject_id="google-alice", email="alice@example.com"),
        registration_cleared=False,
    )

    assert user.id == existing.id


def test_sign_in_returns_existing_user_by_email():
    storage = InMemoryRadspionStorage()
    existing = storage.create_user(
        email="alice@example.com",
        google_subject_id="google-alice",
        display_name="Alice",
    )
    app = Radspion(storage)

    user = app.sign_in_with_google(
        _profile(google_subject_id="google-other", email="alice@example.com"),
        registration_cleared=False,
    )

    assert user.id == existing.id


def test_sign_in_provisions_new_user_when_registration_cleared():
    storage = InMemoryRadspionStorage()
    app = Radspion(storage)

    user = app.sign_in_with_google(_profile(), registration_cleared=True)

    assert user.email == "new@example.com"
    assert storage.user_in_group(user.id, ORIENTATION_GROUP_ID)


def test_sign_in_rejects_new_user_without_registration_cleared():
    storage = InMemoryRadspionStorage()
    app = Radspion(storage)

    with pytest.raises(SignupNotAllowedError):
        app.sign_in_with_google(_profile(), registration_cleared=False)


def test_sign_in_raises_when_orientation_group_missing():
    storage = InMemoryRadspionStorage()

    def no_orientation():
        return None

    storage.get_orientation_group_id = no_orientation  # type: ignore[method-assign]
    app = Radspion(storage)

    with pytest.raises(RuntimeError, match="Orientation group"):
        app.sign_in_with_google(_profile(), registration_cleared=True)
