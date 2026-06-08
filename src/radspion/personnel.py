"""Agent Personnel File view models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ServiceRecordEntry:
    """One line on the agent service record."""

    occurred_at: str
    verb: str
    detail: str


@dataclass(frozen=True)
class PersonnelFile:
    """Read model for the Agent Personnel File page."""

    display_name: str
    email: str
    codename: str
    recruited_at: str
    missions_completed: int
    active_missions: int
    service_record: tuple[ServiceRecordEntry, ...]


def format_personnel_date(iso_timestamp: str) -> tuple[str, str]:
    """Return (HTML datetime attr, display label) from a SQLite datetime string."""
    normalized = iso_timestamp.replace(" ", "T", 1)
    if "T" not in normalized:
        normalized = f"{normalized}T00:00:00"
    dt = datetime.fromisoformat(normalized)
    return dt.date().isoformat(), f"{dt.strftime('%b')} {dt.day}, {dt.year}"
