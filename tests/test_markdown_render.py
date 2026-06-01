"""Tests for mission markdown rendering."""

from radspion.markdown_render import render_mission_markdown


def test_render_mission_markdown_includes_fenced_code():
    source = "# Title\n\n```bash\necho hi\n```\n"
    html = str(render_mission_markdown(source))
    assert "<pre>" in html or "<code>" in html
    assert "echo hi" in html
