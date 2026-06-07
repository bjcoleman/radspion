"""Server-side rendering for mission Brief / Debrief markdown."""

import markdown
from markupsafe import Markup

from radspion.markdown_collapsible import parse_mission_markdown, render_segments_html
from radspion.markdown_themes import resolve_markdown_theme

_EXTENSIONS = [
    "pymdownx.highlight",
    "pymdownx.superfences",
    "markdown.extensions.sane_lists",
    "markdown.extensions.tables",
]


def _render_markdown_core(source: str, *, theme_key: str | None = None) -> str:
    """Convert one markdown fragment to HTML (no collapsible preprocessing)."""
    theme = resolve_markdown_theme(theme_key)
    extension_configs = {
        "pymdownx.highlight": {
            "pygments_style": theme.pygments_style,
        },
    }
    return markdown.markdown(
        source,
        extensions=_EXTENSIONS,
        extension_configs=extension_configs,
    )


def render_mission_markdown(source: str, *, theme_key: str | None = None) -> Markup:
    """Convert mission markdown to safe HTML for Jinja."""
    parts = parse_mission_markdown(source)
    html = render_segments_html(
        parts,
        lambda fragment: _render_markdown_core(fragment, theme_key=theme_key),
    )
    return Markup(html)
