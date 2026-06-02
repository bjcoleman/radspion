"""Tests for the Radspion application layer."""

from radspion.radspion import Radspion
from tests.fakes.storage import InMemoryRadspionStorage


def test_redeem_unlock_code_rejects_empty_after_trim():
    app = Radspion(InMemoryRadspionStorage())

    result = app.redeem_unlock_code(1, "   ")

    assert result.outcome == "invalid"
    assert result.new_missions == ()
    assert result.message is None


def test_submit_mission_completion_rejects_empty_after_trim():
    app = Radspion(InMemoryRadspionStorage())

    result = app.submit_mission_completion(1, "es-beta", "   ")

    assert result.outcome == "invalid"
    assert result.new_missions == ()
    assert result.message is None


def test_find_listed_mission_delegates_to_storage():
    app = Radspion(InMemoryRadspionStorage())

    assert app.find_listed_mission(1, "es-alpha") is None
