"""Application (business) layer for Radspion."""


class Radspion:
    """Business logic; uses a storage implementation for persistence."""

    def __init__(self, storage) -> None:
        self._storage = storage

    def validate_registration_code(self, raw_code: str) -> bool:
        """
        Validate a registration access code.

        Trims whitespace; comparison is case-sensitive.
        """
        code = raw_code.strip()
        if not code:
            return False
        return self._storage.registration_code_exists(code)
