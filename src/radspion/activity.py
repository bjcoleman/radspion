"""Field Activity page view models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

ORIENTATION_GROUP_NAME = "Orientation"


@dataclass(frozen=True)
class ActivityLeaderboardEntry:
    """One row on the Top Agents list."""

    rank: int
    codename: str
    completed_count: int


@dataclass(frozen=True)
class ActivityStorylineEntry:
    """One row on the Storylines list."""

    name: str
    mission_count: int
    never_completed: int
    never_assigned: int


@dataclass(frozen=True)
class ActivityFeedEntry:
    """One row on a recent-activity feed."""

    codename: str
    storyline_name: str
    occurred_at: str


@dataclass(frozen=True)
class FieldActivity:
    """Read model for the public Field Activity page."""

    top_agents: tuple[ActivityLeaderboardEntry, ...]
    storylines: tuple[ActivityStorylineEntry, ...]
    recent_clearances: tuple[ActivityFeedEntry, ...]
    recent_completions: tuple[ActivityFeedEntry, ...]


def storyline_meta(entry: ActivityStorylineEntry) -> str:
    """Build the grey meta line for a storyline row."""
    parts = [f"{entry.mission_count} missions"]
    if entry.never_completed:
        parts.append(f"{entry.never_completed} never completed")
    if entry.never_assigned:
        parts.append(f"{entry.never_assigned} never assigned")
    return " · ".join(parts)


def sort_storylines(entries: list[ActivityStorylineEntry]) -> tuple[ActivityStorylineEntry, ...]:
    """Never-assigned ascending; Orientation always last; ties by name."""
    return tuple(
        sorted(
            entries,
            key=lambda entry: (
                entry.name == ORIENTATION_GROUP_NAME,
                entry.never_assigned,
                entry.name.casefold(),
            ),
        )
    )


def format_activity_relative_time(
    iso_timestamp: str,
    *,
    now: datetime | None = None,
) -> tuple[str, str]:
    """Return (HTML datetime attr, short relative label) from a SQLite datetime string."""
    normalized = iso_timestamp.replace(" ", "T", 1)
    if "T" not in normalized:
        normalized = f"{normalized}T00:00:00"
    occurred = datetime.fromisoformat(normalized)
    if occurred.tzinfo is None:
        occurred = occurred.replace(tzinfo=UTC)
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    delta = current - occurred.astimezone(UTC)
    seconds = max(0, int(delta.total_seconds()))

    if seconds < 60:
        label = "now"
    elif seconds < 3600:
        label = f"{seconds // 60}m"
    elif seconds < 86400:
        label = f"{seconds // 3600}h"
    else:
        label = f"{seconds // 86400}d"

    return occurred.isoformat(timespec="seconds"), label
