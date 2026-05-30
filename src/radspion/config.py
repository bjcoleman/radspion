"""Application configuration from environment variables."""

from dataclasses import dataclass
from os import getenv
from pathlib import Path

_DEFAULT_DATABASE = Path("database") / "radspion.db"
_TEST_SECRET_KEY = "test-secret-key-not-for-production"


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""


_TEST_BASE_URL = "http://localhost:8000"
_TEST_GOOGLE_CLIENT_ID = "test-google-client-id"
_TEST_GOOGLE_CLIENT_SECRET = "test-google-client-secret"


@dataclass(frozen=True)
class Config:
    """Settings used at application startup."""

    database_path: Path
    secret_key: str
    base_url: str
    google_client_id: str
    google_client_secret: str
    testing: bool = False


def load_config(*, testing: bool = False) -> Config:
    """Load configuration from the current process environment."""
    if testing:
        secret_key = _TEST_SECRET_KEY
        base_url = _TEST_BASE_URL
        google_client_id = _TEST_GOOGLE_CLIENT_ID
        google_client_secret = _TEST_GOOGLE_CLIENT_SECRET
    else:
        secret_key = getenv("SECRET_KEY")
        if not secret_key:
            raise ConfigurationError(
                "SECRET_KEY is required. Set it in the environment or .env "
                '(e.g. python3 -c "import secrets; print(secrets.token_urlsafe(32))").'
            )
        base_url = getenv("BASE_URL")
        if not base_url:
            raise ConfigurationError("BASE_URL is required.")
        google_client_id = getenv("GOOGLE_CLIENT_ID")
        if not google_client_id:
            raise ConfigurationError("GOOGLE_CLIENT_ID is required.")
        google_client_secret = getenv("GOOGLE_CLIENT_SECRET")
        if not google_client_secret:
            raise ConfigurationError("GOOGLE_CLIENT_SECRET is required.")

    database_path = Path(getenv("DATABASE_PATH", str(_DEFAULT_DATABASE)))

    return Config(
        database_path=database_path,
        secret_key=secret_key,
        base_url=base_url,
        google_client_id=google_client_id,
        google_client_secret=google_client_secret,
        testing=testing,
    )
