"""Tests for collapsible mission markdown sections."""

import pytest

from radspion.markdown_collapsible import (
    MarkdownPart,
    collect_section_body,
    escape_html,
    parse_mission_markdown,
    render_collapsible_section,
    render_segments_html,
    validate_collapsible_markdown,
)

CHEVRON_STUB = '<span class="mission-group__chevron">stub</span>'


def test_parse_empty_source():
    assert parse_mission_markdown("") == []


def test_parse_plain_markdown_single_segment():
    parts = parse_mission_markdown("## Visible\n\nHello.\n")
    assert len(parts) == 1
    assert parts[0].kind == "markdown"
    assert "## Visible" in parts[0].source


def test_parse_collapsible_section_until_next_heading():
    source = """## Intro

Read now.

## Later ???

Hidden body.

## After

Visible again.
"""
    parts = parse_mission_markdown(source)
    assert [part.kind for part in parts] == ["markdown", "collapsible", "markdown"]
    assert parts[1].title == "Later"
    assert parts[1].level == 2
    assert "Hidden body." in parts[1].source
    assert "## After" in parts[2].source


def test_parse_collapsible_stops_at_hr():
    source = """## Later ???

Hidden.

---

Footer text.
"""
    parts = parse_mission_markdown(source)
    assert [part.kind for part in parts] == ["collapsible", "hr", "markdown"]
    assert parts[2].source.strip() == "Footer text."


def test_parse_prose_horizontal_rule():
    parts = parse_mission_markdown("Intro.\n\n---\n\nFooter.\n")
    assert [part.kind for part in parts] == ["markdown", "hr", "markdown"]


def test_parse_hint_sections_after_hr():
    source = """## Fieldwork ???

Do the work.

---

### Hint 1 ???

First hint.

### Hint 2 ???

Second hint.

---

Submit line.
"""
    parts = parse_mission_markdown(source)
    assert [part.kind for part in parts] == [
        "collapsible",
        "hr",
        "collapsible",
        "collapsible",
        "hr",
        "markdown",
    ]
    assert parts[2].title == "Hint 1"
    assert parts[2].level == 3
    assert parts[3].title == "Hint 2"


def test_parse_ignores_collapsible_marker_inside_fence():
    source = """## Real ???

```markdown
## Fake ???
```

Body.
"""
    parts = parse_mission_markdown(source)
    assert len(parts) == 1
    assert parts[0].kind == "collapsible"
    assert "## Fake ???" in parts[0].source


@pytest.mark.parametrize(
    ("lines", "start", "trigger_level", "in_fence", "expected_body", "expected_end", "hr_after"),
    [
        (["body\n", "## Stop\n"], 0, 2, False, ["body\n"], 1, False),
        (["body\n", "---\n", "tail\n"], 0, 2, False, ["body\n"], 2, True),
        (
            ["```\n", "## Not a boundary\n", "```\n", "kept\n"],
            0,
            2,
            False,
            ["```\n", "## Not a boundary\n", "```\n", "kept\n"],
            4,
            False,
        ),
    ],
)
def test_collect_section_body_boundaries(
    lines: list[str],
    start: int,
    trigger_level: int,
    in_fence: bool,
    expected_body: list[str],
    expected_end: int,
    hr_after: bool,
):
    body, end, found_hr, _ = collect_section_body(lines, start, trigger_level, in_fence)
    assert body == expected_body
    assert end == expected_end
    assert found_hr is hr_after


@pytest.mark.parametrize(
    ("source", "needle"),
    [
        ("# Title ???\n\nBody.\n", "only allowed on ## and ###"),
        ("#### Title ???\n\nBody.\n", "only allowed on ## and ###"),
    ],
)
def test_validate_rejects_invalid_heading_levels(source: str, needle: str):
    errors = validate_collapsible_markdown(source, path="brief.md")
    assert any(needle in error for error in errors)


def test_validate_rejects_nested_collapsible():
    source = """## Outer ???

### Inner ???

Nope.
"""
    errors = validate_collapsible_markdown(source, path="brief.md")
    assert any("nested inside" in error for error in errors)


def test_validate_rejects_empty_collapsible_body():
    source = "## Empty ???\n\n## Next\n"
    errors = validate_collapsible_markdown(source, path="brief.md")
    assert any("has no body content" in error for error in errors)


def test_validate_exits_nested_section_at_horizontal_rule():
    source = """## Outer ???

### Inner

---

### Hint ???

Still fine.
"""
    errors = validate_collapsible_markdown(source, path="brief.md")
    assert not any("nested inside" in error for error in errors)


def test_validate_exits_nested_section_at_peer_heading():
    source = """## Outer ???

### Inner

## Next section

### Hint ???

Still fine.
"""
    errors = validate_collapsible_markdown(source, path="brief.md")
    assert not any("nested inside" in error for error in errors)


def test_validate_ignores_invalid_marker_inside_fence():
    source = """```markdown
# Bad ???
```
"""
    assert validate_collapsible_markdown(source) == []


def test_escape_html():
    assert escape_html('Tom & "Jerry" <script>') == "Tom &amp; &quot;Jerry&quot; &lt;script&gt;"


def test_render_collapsible_html_includes_details_and_chevron():
    parts = parse_mission_markdown("## Later ???\n\nHidden.\n")
    html = render_segments_html(
        parts,
        lambda source: f"<p>{source.strip()}</p>",
        chevron_html=CHEVRON_STUB,
    )
    assert "<details" in html
    assert 'class="brief-section brief-section--level2"' in html
    assert "<h2>Later</h2>" in html
    assert CHEVRON_STUB in html
    assert "Hidden." in html


def test_render_collapsible_section_level3_and_empty_body():
    part = MarkdownPart(kind="collapsible", source="   \n", title="Hint", level=3)

    def render(_source: str) -> str:
        return "<p>nope</p>"

    html = render_collapsible_section(part, render, chevron_html=CHEVRON_STUB)
    assert "brief-section--level3" in html
    assert "<h3>Hint</h3>" in html
    assert "<p>nope</p>" not in html


def test_render_collapsible_section_escapes_title():
    part = MarkdownPart(kind="collapsible", source="Body", title="A & B", level=2)
    html = render_collapsible_section(part, lambda source: source, chevron_html=CHEVRON_STUB)
    assert "<h2>A &amp; B</h2>" in html
