"""Resolve paths within the radspion repository checkout.

Layout contract (all paths relative to the repo root):

- ``src/radspion/`` — Python package
- ``database/`` — default SQLite database directory
- ``.env`` — local configuration (not committed)
- ``pyproject.toml`` — marks the repository root
"""

from __future__ import annotations

from os import getenv
from pathlib import Path

from dotenv import load_dotenv

_DEFAULT_DATABASE = Path("database") / "radspion.db"


def project_root() -> Path:
    """Return the radspion repository root directory."""
    candidate = Path(__file__).resolve().parent
    for directory in (candidate, *candidate.parents):
        if (directory / "pyproject.toml").is_file() and (directory / "src" / "radspion").is_dir():
            return directory
    raise RuntimeError("Could not locate radspion repository root from installed package")


def load_tool_env() -> None:
    """Load ``.env`` from the repository root into the process environment."""
    load_dotenv(project_root() / ".env")


def sql_dir() -> Path:
    return project_root() / "src" / "radspion" / "sql"


def schema_path() -> Path:
    return sql_dir() / "schema.sql"


def testing_seed_path() -> Path:
    return sql_dir() / "seed_testing_storyline.sql"


def database_path() -> Path:
    """Resolve ``DATABASE_PATH`` from the environment (default: ``database/radspion.db``)."""
    load_tool_env()
    raw = getenv("DATABASE_PATH", str(_DEFAULT_DATABASE)).strip()
    path = Path(raw)
    if not path.is_absolute():
        path = (project_root() / path).resolve()
    return path
