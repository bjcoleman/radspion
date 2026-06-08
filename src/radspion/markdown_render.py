"""Server-side rendering for mission Brief / Debrief markdown."""

import markdown
from markupsafe import Markup

from radspion.markdown_collapsible import parse_mission_markdown, render_segments_html

_EXTENSIONS = [
    "pymdownx.highlight",
    "pymdownx.superfences",
    "markdown.extensions.sane_lists",
    "markdown.extensions.tables",
]

_EXTENSION_CONFIGS = {
    "pymdownx.highlight": {
        "pygments_style": "native",
    },
}


def _render_markdown_core(source: str) -> str:
    """Convert one markdown fragment to HTML (no collapsible preprocessing)."""
    return markdown.markdown(
        source,
        extensions=_EXTENSIONS,
        extension_configs=_EXTENSION_CONFIGS,
    )


def render_mission_markdown(source: str) -> Markup:
    """Convert mission markdown to safe HTML for Jinja."""
    parts = parse_mission_markdown(source)
    html = render_segments_html(parts, _render_markdown_core)
    return Markup(html)
