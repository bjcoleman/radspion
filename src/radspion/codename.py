"""Codename validation and update results."""

from dataclasses import dataclass

CODENAME_MIN_LEN = 4
CODENAME_MAX_LEN = 20

INVALID_LENGTH_MESSAGE = "Codenames must be 4–20 characters."
DUPLICATE_CODENAME_MESSAGE = "Another agent is using this codename."
SUCCESS_MESSAGE = "Your codename has been updated."


def codename_length_valid(codename: str) -> bool:
    """Return True when codename length is within allowed bounds (Unicode code points)."""
    length = len(codename)
    return CODENAME_MIN_LEN <= length <= CODENAME_MAX_LEN


@dataclass(frozen=True)
class CodenameUpdateResult:
    """Result of POST /api/codename."""

    outcome: str  # success | invalid
    message: str | None = None

    def to_api_dict(self) -> dict:
        """Serialize for POST /api/codename responses."""
        data: dict = {"outcome": self.outcome}
        if self.message is not None:
            data["message"] = self.message
        return data
