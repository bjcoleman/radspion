"""Tests for static platform copy under content/."""

from radspion.content_files import load_welcome_memo_markdown, welcome_memo_path
from radspion.project_paths import project_root


def test_welcome_memo_path_is_under_repo_content():
    assert welcome_memo_path() == project_root() / "content" / "welcome.md"


def test_load_welcome_memo_markdown_reads_repo_file():
    source = load_welcome_memo_markdown()

    assert source is not None
    assert "Director of Agent Development" in source
    assert "Stay Observant" in source
