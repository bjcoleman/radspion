"""Server-side rendering for mission Brief / Debrief markdown."""

import markdown
from markupsafe import Markup

_EXTENSIONS = ["fenced_code", "sane_lists", "tables"]


def render_mission_markdown(source: str) -> Markup:
    """Convert mission markdown to safe HTML for Jinja."""
    html = markdown.markdown(source, extensions=_EXTENSIONS)
    return Markup(html)
