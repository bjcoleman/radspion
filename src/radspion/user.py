"""Agent user record."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Row from users."""

    id: int
    email: str
    google_subject_id: str
    display_name: str
    is_operator: bool = False
