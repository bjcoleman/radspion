"""Application configuration from environment variables."""

from dataclasses import dataclass
from os import getenv
from pathlib import Path

_DEFAULT_DATABASE = Path("database") / "radspion.db"
_TEST_SECRET_KEY = "test-secret-key-not-for-production"


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    """Settings used at application startup."""

    database_path: Path
    secret_key: str
    testing: bool = False


def load_config(*, testing: bool = False) -> Config:
    """Load configuration from the current process environment."""
    if testing:
        secret_key = _TEST_SECRET_KEY
    else:
        secret_key = getenv("SECRET_KEY")
        if not secret_key:
            raise ConfigurationError(
                "SECRET_KEY is required. Set it in the environment or .env "
                '(e.g. python3 -c "import secrets; print(secrets.token_urlsafe(32))").'
            )

    database_path = Path(getenv("DATABASE_PATH", str(_DEFAULT_DATABASE)))

    return Config(
        database_path=database_path,
        secret_key=secret_key,
        testing=testing,
    )
