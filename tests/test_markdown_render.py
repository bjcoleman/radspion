"""Tests for mission markdown rendering."""

from radspion.markdown_render import render_mission_markdown


def test_render_mission_markdown_fenced_code_with_language():
    source = "# Title\n\n```python\necho hi\n```\n"
    html = str(render_mission_markdown(source))
    assert '<div class="highlight">' in html
    assert "<pre>" in html
    assert '<span class="n">echo</span>' in html
    assert '<span class="k">' in html or '<span class="n">' in html


def test_render_mission_markdown_fenced_code_without_language():
    source = "```\nplain text\n```\n"
    html = str(render_mission_markdown(source))
    assert '<div class="highlight">' in html
    assert "plain text" in html
    assert '<span class="k">' not in html


def test_render_mission_markdown_collapsible_section():
    source = """## Visible

Now.

## Later ???

Hidden paragraph.

---

Footer.
"""
    html = str(render_mission_markdown(source))
    assert "<details" in html
    assert "<h2>Later</h2>" in html
    assert 'class="mission-group__chevron"' in html
    assert "<p>Hidden paragraph.</p>" in html
    assert "<hr>" in html
    assert "<p>Footer.</p>" in html
    assert "Hidden paragraph." not in html[: html.index("<details")]


def test_render_mission_markdown_fenced_code_inside_list():
    source = """* First

    ```python
    def foo():
        pass
    ```

* Second
"""
    html = str(render_mission_markdown(source))
    assert html.count("<ul>") == 1
    assert '<div class="highlight">' in html
    assert "<pre>" in html
    assert '<span class="k">def</span>' in html
