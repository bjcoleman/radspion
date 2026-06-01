"""Tests for the Radspion application layer."""

from radspion.radspion import Radspion
from tests.fakes.storage import InMemoryRadspionStorage


def test_validate_registration_code_accepts_known_code():
    app = Radspion(InMemoryRadspionStorage({"SECRET-CODE"}))

    assert app.validate_registration_code("SECRET-CODE") is True


def test_validate_registration_code_trims_whitespace():
    app = Radspion(InMemoryRadspionStorage({"SECRET-CODE"}))

    assert app.validate_registration_code("  SECRET-CODE \n") is True


def test_validate_registration_code_is_case_sensitive():
    app = Radspion(InMemoryRadspionStorage({"SECRET-CODE"}))

    assert app.validate_registration_code("secret-code") is False


def test_validate_registration_code_rejects_unknown_code():
    app = Radspion(InMemoryRadspionStorage({"SECRET-CODE"}))

    assert app.validate_registration_code("WRONG") is False


def test_validate_registration_code_rejects_empty_after_trim():
    app = Radspion(InMemoryRadspionStorage({"SECRET-CODE"}))

    assert app.validate_registration_code("   ") is False


def test_redeem_unlock_code_rejects_empty_after_trim():
    app = Radspion(InMemoryRadspionStorage())

    result = app.redeem_unlock_code(1, "   ")

    assert result.outcome == "invalid"
    assert result.new_missions == ()
    assert result.message is None
