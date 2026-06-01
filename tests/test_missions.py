"""Tests for mission dashboard view models."""

from radspion.missions import DashboardGroup, DashboardMission


def test_counts_label_includes_active_and_completed():
    group = DashboardGroup(
        id=1,
        name="Testing Storyline",
        missions=[
            DashboardMission("es-beta", "ES: Beta", "active"),
            DashboardMission("es-gamma", "ES: Gamma", "active"),
            DashboardMission("es-alpha", "ES: Alpha", "completed"),
        ],
    )

    assert group.counts_label() == "2 active · 1 completed"


def test_counts_label_marks_completed_hidden_when_toggle_off():
    group = DashboardGroup(
        id=1,
        name="Testing Storyline",
        missions=[
            DashboardMission("es-beta", "ES: Beta", "active"),
            DashboardMission("es-gamma", "ES: Gamma", "active"),
            DashboardMission("es-alpha", "ES: Alpha", "completed"),
        ],
    )

    assert group.counts_label(show_completed=False) == "2 active · 1 completed (hidden)"


def test_counts_label_completed_only_hidden():
    group = DashboardGroup(
        id=2,
        name="Orientation",
        missions=[
            DashboardMission("basic-training", "Welcome to Radspion", "completed"),
        ],
    )

    assert group.counts_label(show_completed=False) == "1 completed (hidden)"
