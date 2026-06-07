"""Tests for shared UI HTML fragments."""

from pathlib import Path

from radspion.ui_fragments import mission_chevron_html


def test_mission_chevron_html_matches_template_file():
    template_path = (
        Path(__file__).resolve().parents[1] / "src/radspion/templates/agent/_mission_chevron.html"
    )
    expected = template_path.read_text(encoding="utf-8").strip()
    assert mission_chevron_html() == expected
    assert 'class="mission-group__chevron"' in mission_chevron_html()
