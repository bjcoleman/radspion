"""Pluggable CSS themes for mission Brief / Debrief markdown rendering."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

_DEFAULT_THEME_KEY = "legacy"


@dataclass(frozen=True)
class MarkdownTheme:
    """Static assets and Pygments settings for one markdown theme."""

    key: str
    label: str
    article_class: str
    stylesheets: tuple[str, ...]
    pygments_style: str
    pygments_css: str
    light_surface: bool = False


MARKDOWN_THEMES: dict[str, MarkdownTheme] = {
    "legacy": MarkdownTheme(
        key="legacy",
        label="Legacy (Radspion dark panel)",
        article_class="markdown",
        stylesheets=("css/markdown/legacy.css",),
        pygments_style="native",
        pygments_css="css/markdown/pygments-native.css",
        light_surface=False,
    ),
    "github-light": MarkdownTheme(
        key="github-light",
        label="GitHub light",
        article_class="markdown-body",
        stylesheets=("css/markdown/vendor/github-markdown-light.css",),
        pygments_style="friendly",
        pygments_css="css/markdown/pygments-friendly.css",
        light_surface=True,
    ),
    "github-dark": MarkdownTheme(
        key="github-dark",
        label="GitHub dark",
        article_class="markdown-body",
        stylesheets=("css/markdown/vendor/github-markdown-dark.css",),
        pygments_style="native",
        pygments_css="css/markdown/pygments-native.css",
        light_surface=False,
    ),
    "latex": MarkdownTheme(
        key="latex",
        label="LaTeX.css (paper)",
        article_class="latex-document",
        stylesheets=("css/markdown/vendor/latex-scoped.css",),
        pygments_style="friendly",
        pygments_css="css/markdown/pygments-friendly.css",
        light_surface=True,
    ),
}

_OVERRIDES_CSS = "css/markdown/radspion-overrides.css"


def default_markdown_theme_key() -> str:
    """Theme key from RADSPION_MARKDOWN_THEME, falling back to legacy."""
    raw = getenv("RADSPION_MARKDOWN_THEME", _DEFAULT_THEME_KEY).strip()
    return raw or _DEFAULT_THEME_KEY


def resolve_markdown_theme(key: str | None = None) -> MarkdownTheme:
    """Return a registered theme, or raise ValueError."""
    resolved = (key or default_markdown_theme_key()).strip()
    try:
        return MARKDOWN_THEMES[resolved]
    except KeyError as exc:
        known = ", ".join(sorted(MARKDOWN_THEMES))
        raise ValueError(f"Unknown markdown theme {resolved!r}. Choose one of: {known}.") from exc


def markdown_stylesheets(theme: MarkdownTheme) -> tuple[str, ...]:
    """Theme CSS plus shared Radspion overrides (always last)."""
    return (*theme.stylesheets, _OVERRIDES_CSS)


def register_markdown_theme_context(app: Flask) -> None:
    """Inject markdown theme data into Jinja templates."""

    @app.context_processor
    def inject_markdown_theme():
        from flask import request

        query_theme = request.args.get("theme") if request else None
        config_theme = app.config.get("MARKDOWN_THEME")
        if query_theme:
            try:
                theme = resolve_markdown_theme(query_theme)
            except ValueError:
                theme = resolve_markdown_theme(config_theme)
        else:
            theme = resolve_markdown_theme(config_theme)
        return {
            "markdown_theme": theme,
            "markdown_stylesheets": markdown_stylesheets(theme),
            "markdown_themes": MARKDOWN_THEMES,
        }
