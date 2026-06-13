"""Load static platform copy from the repository content/ directory."""

from __future__ import annotations

import logging
from pathlib import Path

from radspion.project_paths import project_root

logger = logging.getLogger(__name__)

WELCOME_MEMO_FILE = "welcome.md"


def welcome_memo_path() -> Path:
    """Path to the dashboard welcome memo markdown file."""
    return project_root() / "content" / WELCOME_MEMO_FILE


def load_welcome_memo_markdown() -> str | None:
    """Read welcome memo source; None if the file is missing."""
    path = welcome_memo_path()
    if not path.is_file():
        logger.warning("Welcome memo not found at %s", path)
        return None
    return path.read_text(encoding="utf-8")
