"""Tests for pluggable mission markdown themes."""

import pytest

from radspion.markdown_themes import (
    MARKDOWN_THEMES,
    markdown_stylesheets,
    resolve_markdown_theme,
)


def test_resolve_markdown_theme_legacy_is_default():
    theme = resolve_markdown_theme(None)
    assert theme.key == "legacy"
    assert theme.article_class == "markdown"


def test_resolve_markdown_theme_github_light():
    theme = resolve_markdown_theme("github-light")
    assert theme.article_class == "markdown-body"
    assert theme.pygments_style == "friendly"


def test_resolve_markdown_theme_latex():
    theme = resolve_markdown_theme("latex")
    assert theme.article_class == "latex-document"
    assert "latex-scoped.css" in theme.stylesheets[0]


def test_resolve_markdown_theme_unknown_raises():
    with pytest.raises(ValueError, match="Unknown markdown theme"):
        resolve_markdown_theme("not-a-theme")


def test_markdown_stylesheets_include_overrides():
    theme = resolve_markdown_theme("github-dark")
    sheets = markdown_stylesheets(theme)
    assert sheets[-1] == "css/markdown/radspion-overrides.css"
    assert sheets[0] in theme.stylesheets


def test_all_registered_themes_have_pygments_css():
    for theme in MARKDOWN_THEMES.values():
        assert theme.pygments_css.startswith("css/markdown/pygments-")
