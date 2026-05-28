"""In-memory storage fakes for tests."""


class InMemoryRadspionStorage:
    """Registration codes held in a set."""

    def __init__(self, registration_codes: set[str] | None = None) -> None:
        self._registration_codes = set(registration_codes or ())

    def registration_code_exists(self, code: str) -> bool:
        return code in self._registration_codes
