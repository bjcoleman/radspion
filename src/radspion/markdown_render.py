"""Server-side rendering for mission Brief / Debrief markdown."""

import markdown
from markupsafe import Markup

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


def render_mission_markdown(source: str) -> Markup:
    """Convert mission markdown to safe HTML for Jinja."""
    html = markdown.markdown(
        source,
        extensions=_EXTENSIONS,
        extension_configs=_EXTENSION_CONFIGS,
    )
    return Markup(html)
