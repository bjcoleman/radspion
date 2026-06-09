"""Tests for create_empty_db CLI."""

from pathlib import Path

import pytest

from radspion.tools.create_empty_db import main


def test_create_empty_db_creates_schema(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "database" / "radspion.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setattr("radspion.project_paths.load_tool_env", lambda: None)

    with pytest.raises(SystemExit) as exc:
        main(["--force"])
    assert exc.value.code == 0
    assert db_path.is_file()

    import sqlite3

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='groups' LIMIT 1",
        ).fetchone()
    assert row is not None


def test_create_empty_db_prompts_on_existing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "data" / "radspion.db"
    db_path.parent.mkdir(parents=True)
    db_path.write_text("old", encoding="utf-8")
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setattr("radspion.project_paths.load_tool_env", lambda: None)
    monkeypatch.setattr("builtins.input", lambda _prompt: "n")

    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 0
    assert db_path.read_text(encoding="utf-8") == "old"
