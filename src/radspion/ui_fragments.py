"""Shared HTML fragments for server-rendered UI (templates and markdown)."""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files

_CHEVRON_PATH = "templates/agent/_mission_chevron.html"


@lru_cache
def mission_chevron_html() -> str:
    """Return the mission-group chevron markup (single source for templates and brief HTML)."""
    return files("radspion").joinpath(_CHEVRON_PATH).read_text(encoding="utf-8").strip()
