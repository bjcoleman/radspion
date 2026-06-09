"""Tests for create_test_db CLI."""

import sqlite3
from pathlib import Path

import pytest

from radspion.tools.create_test_db import main
from tests.helpers import SAMPLE_AGENTS


def test_create_test_db_loads_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "radspion.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setattr("radspion.project_paths.load_tool_env", lambda: None)
    monkeypatch.setattr("radspion.tools.create_test_db.load_tool_env", lambda: None)

    with pytest.raises(SystemExit) as exc:
        main(["--force"])
    assert exc.value.code == 0

    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        row = conn.execute(
            "SELECT COUNT(*) FROM missions WHERE slug LIKE 'es-%'",
        ).fetchone()
        mission_count = row[0] if row else 0
    assert count == 4
    assert mission_count == 5


def test_create_test_db_bind_dev_email(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "radspion.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("DEV_EMAIL", "dev@example.com")
    monkeypatch.setattr("radspion.project_paths.load_tool_env", lambda: None)
    monkeypatch.setattr("radspion.tools.create_test_db.load_tool_env", lambda: None)

    with pytest.raises(SystemExit) as exc:
        main(["--force", "--bind-dev-email"])
    assert exc.value.code == 0

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT email, display_name FROM users WHERE id = ?",
            (SAMPLE_AGENTS["alice"]["id"],),
        ).fetchone()
    assert row == ("dev@example.com", "Developer")


def test_create_test_db_bind_dev_email_requires_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    db_path = tmp_path / "radspion.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.delenv("DEV_EMAIL", raising=False)
    monkeypatch.setattr("radspion.project_paths.load_tool_env", lambda: None)
    monkeypatch.setattr("radspion.tools.create_test_db.load_tool_env", lambda: None)

    with pytest.raises(SystemExit) as exc:
        main(["--force", "--bind-dev-email"])
    assert exc.value.code == 1
