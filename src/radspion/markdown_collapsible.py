"""Collapsible sections in mission brief/debrief markdown (## / ### with ??? suffix)."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Literal

from radspion.ui_fragments import mission_chevron_html

COLLAPSE_SUFFIX = " ???"
_COLLAPSE_HEADING = re.compile(r"^(#{2,3})\s+(.+?)\s+\?\?\?\s*$")
_INVALID_COLLAPSE_HEADING = re.compile(r"^(#|#{4,6})\s+(.+?)\s+\?\?\?\s*$")
_HEADING_LEVEL = re.compile(r"^(#{1,6})\s+")
_HR_LINE = re.compile(r"^---\s*$")


@dataclass(frozen=True)
class MarkdownPart:
    """One rendered unit from a mission markdown document."""

    kind: Literal["markdown", "collapsible", "hr"]
    source: str = ""
    title: str | None = None
    level: int | None = None
    heading_line: int | None = None
    body_start_line: int | None = None


def _is_fence_line(line: str) -> bool:
    return line.strip().startswith("```")


def _heading_level(line: str) -> int | None:
    match = _HEADING_LEVEL.match(line)
    if match is None:
        return None
    return len(match.group(1))


def _parse_collapsible_heading(line: str) -> tuple[int, str] | None:
    match = _COLLAPSE_HEADING.match(line)
    if match is None:
        return None
    return len(match.group(1)), match.group(2)


def collect_section_body(
    lines: list[str],
    start: int,
    trigger_level: int,
    in_fence: bool,
) -> tuple[list[str], int, bool, bool]:
    """Collect lines belonging to a collapsible section body.

      Returns ``(body_lines, end_index, hr_after, in_fence)``.
    ``end_index`` is the index of the first line after the body (boundary line
      when ``hr_after`` is false).
    """
    body: list[str] = []
    position = start
    while position < len(lines):
        line = lines[position]
        if _is_fence_line(line):
            in_fence = not in_fence
            body.append(line)
            position += 1
            continue
        if in_fence:
            body.append(line)
            position += 1
            continue
        if _HR_LINE.match(line):
            return body, position + 1, True, in_fence
        level = _heading_level(line)
        if level is not None and level <= trigger_level:
            return body, position, False, in_fence
        body.append(line)
        position += 1
    return body, position, False, in_fence


def _iter_invalid_collapse_headings(source: str) -> Iterable[tuple[int, str]]:
    """Yield ``(line_number, title)`` for `` ???`` markers on invalid heading levels."""
    in_fence = False
    for line_number, line in enumerate(source.splitlines(), start=1):
        if _is_fence_line(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = _INVALID_COLLAPSE_HEADING.match(line)
        if match is not None:
            yield line_number, match.group(2)


def _first_nested_collapsible_in_body(body: str) -> tuple[int, str] | None:
    """Return ``(body_line_number, title)`` for the first nested `` ???`` heading."""
    in_fence = False
    for line_number, line in enumerate(body.splitlines(), start=1):
        if _is_fence_line(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        collapsible = _parse_collapsible_heading(line)
        if collapsible is not None:
            return line_number, collapsible[1]
    return None


def parse_mission_markdown(source: str) -> list[MarkdownPart]:
    """Split mission markdown into prose, collapsible sections, and horizontal rules."""
    if not source:
        return []

    lines = source.splitlines(keepends=True)
    parts: list[MarkdownPart] = []
    prose_buf: list[str] = []
    in_fence = False
    index = 0

    def flush_prose() -> None:
        if not prose_buf:
            return
        text = "".join(prose_buf)
        prose_buf.clear()
        if text.strip():
            parts.append(MarkdownPart(kind="markdown", source=text))

    while index < len(lines):
        line = lines[index]
        if _is_fence_line(line):
            in_fence = not in_fence
            prose_buf.append(line)
            index += 1
            continue

        if not in_fence:
            collapsible = _parse_collapsible_heading(line)
            if collapsible is not None:
                flush_prose()
                heading_line = index + 1
                level, title = collapsible
                index += 1
                body_start_line = index + 1
                body_lines, index, hr_after, in_fence = collect_section_body(
                    lines,
                    index,
                    level,
                    in_fence,
                )
                parts.append(
                    MarkdownPart(
                        kind="collapsible",
                        source="".join(body_lines),
                        title=title,
                        level=level,
                        heading_line=heading_line,
                        body_start_line=body_start_line,
                    ),
                )
                if hr_after:
                    parts.append(MarkdownPart(kind="hr"))
                continue

            if _HR_LINE.match(line):
                flush_prose()
                parts.append(MarkdownPart(kind="hr"))
                index += 1
                continue

        prose_buf.append(line)
        index += 1

    flush_prose()
    return parts


def validate_collapsible_markdown(source: str, *, path: str = "") -> list[str]:
    """Return lint messages for collapsible-section authoring mistakes."""
    prefix = f"{path}:" if path else ""
    errors: list[str] = []

    for line_number, _title in _iter_invalid_collapse_headings(source):
        errors.append(
            f"{prefix}{line_number}: collapsible marker {COLLAPSE_SUFFIX!r} "
            "is only allowed on ## and ### headings",
        )

    for part in parse_mission_markdown(source):
        if part.kind != "collapsible":
            continue

        if not part.source.strip():
            errors.append(
                f"{prefix}{part.heading_line}: collapsible section {part.title!r} "
                "has no body content",
            )

        nested = _first_nested_collapsible_in_body(part.source)
        if nested is not None and part.body_start_line is not None:
            nested_body_line, nested_title = nested
            nested_line = part.body_start_line + nested_body_line - 1
            errors.append(
                f"{prefix}{nested_line}: collapsible heading {nested_title!r} is nested inside "
                f"another collapsible section; add --- or an intervening ## heading",
            )

    return errors


def render_segments_html(
    parts: Iterable[MarkdownPart],
    render_markdown: Callable[[str], str],
    *,
    chevron_html: str | None = None,
) -> str:
    """Render parsed parts to HTML, wrapping collapsible sections in <details>."""
    chunks: list[str] = []
    chevron = chevron_html if chevron_html is not None else mission_chevron_html()

    for part in parts:
        if part.kind == "hr":
            chunks.append("<hr>")
            continue
        if part.kind == "markdown":
            if part.source.strip():
                chunks.append(render_markdown(part.source))
            continue
        if part.kind == "collapsible":
            chunks.append(
                render_collapsible_section(part, render_markdown, chevron_html=chevron),
            )

    return "".join(chunks)


def render_collapsible_section(
    part: MarkdownPart,
    render_markdown: Callable[[str], str],
    *,
    chevron_html: str,
) -> str:
    """Render one collapsible section to HTML."""
    level_class = "brief-section--level2" if part.level == 2 else "brief-section--level3"
    heading_tag = f"h{part.level}"
    title = part.title or ""
    body_html = render_markdown(part.source) if part.source.strip() else ""
    return (
        f'<details class="brief-section {level_class}">'
        '<summary class="brief-section__summary">'
        f"{chevron_html}"
        f"<{heading_tag}>{escape_html(title)}</{heading_tag}>"
        f"</summary>{body_html}</details>"
    )


def escape_html(text: str) -> str:
    """Escape text for use inside HTML elements."""
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )
