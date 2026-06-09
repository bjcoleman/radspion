"""Tests for storyline deletion and delete_storyline CLI."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from radspion.storyline_delete import (
    StorylineDeleteAborted,
    StorylineDeleteError,
    confirm_delete_group_name,
    format_delete_report,
    load_delete_impact,
)
from radspion.tools.delete_storyline import delete_storyline, main
from radspion.tools.seed_storyline import seed_storyline
from tests.helpers import load_schema_only, write_minimal_pack


def _seed_group(db_path: Path, pack_root: Path) -> None:
    load_schema_only(db_path)
    seed_storyline(pack_root, database_path_loader=lambda: db_path)


def _insert_agent_status(
    db_path: Path,
    *,
    email: str,
    slug: str,
    status: str,
) -> None:
    with sqlite3.connect(db_path) as conn:
        user_id = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if user_id is None:
            conn.execute(
                """
                INSERT INTO users (
                    email, google_subject_id, display_name, codename
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    email,
                    f"google-{email}",
                    email.split("@")[0].title(),
                    email.split("@")[0].title(),
                ),
            )
            user_id = conn.execute("SELECT last_insert_rowid()").fetchone()
        mission_id = conn.execute(
            "SELECT id FROM missions WHERE slug = ?",
            (slug,),
        ).fetchone()[0]
        conn.execute(
            """
            INSERT INTO agent_mission_status (
                user_id, mission_id, status, listed_via
            ) VALUES (?, ?, ?, 'open')
            """,
            (user_id[0], mission_id, status),
        )
        conn.commit()


def test_check_reports_impact(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_group(db_path, pack_root)
    _insert_agent_status(
        db_path,
        email="alice@example.com",
        slug="alpha",
        status="active",
    )
    _insert_agent_status(
        db_path,
        email="bob@example.com",
        slug="alpha",
        status="completed",
    )
    monkeypatch.setattr(
        "radspion.tools.delete_storyline.resolve_database_path",
        lambda: db_path,
    )

    with pytest.raises(SystemExit) as exc:
        main(["Test Group", "--check"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "Storyline: 'Test Group' (1 mission)" in captured.out
    assert "alpha: 2 agent rows (1 active, 1 completed)" in captured.out
    assert "Totals: 2 agent rows (1 active, 1 completed) across 2 agents" in captured.out


def test_delete_requires_typed_confirmation(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_group(db_path, pack_root)

    with pytest.raises(StorylineDeleteAborted):
        delete_storyline(
            "Test Group",
            is_tty=False,
            database_path_loader=lambda: db_path,
        )

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM groups WHERE name = 'Test Group'",
        ).fetchone()
    assert row is not None


def test_delete_prints_report_before_confirm(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_group(db_path, pack_root)
    prompts: list[str] = []

    def fake_input(prompt: str) -> str:
        prompts.append(prompt)
        return "Test Group"

    monkeypatch.setattr("builtins.input", fake_input)

    delete_storyline(
        "Test Group",
        is_tty=True,
        database_path_loader=lambda: db_path,
    )
    captured = capsys.readouterr()
    assert "Storyline: 'Test Group' (1 mission)" in captured.out
    assert prompts
    assert "Type 'Test Group' to confirm:" in prompts[0]
    assert "delete storyline 'Test Group'" in prompts[0]


def test_delete_with_yes_removes_storyline(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_group(db_path, pack_root)
    _insert_agent_status(
        db_path,
        email="alice@example.com",
        slug="alpha",
        status="completed",
    )

    result = delete_storyline(
        "Test Group",
        auto_yes=True,
        database_path_loader=lambda: db_path,
    )
    assert result.applied is True

    with sqlite3.connect(db_path) as conn:
        groups = conn.execute(
            "SELECT COUNT(*) FROM groups WHERE name = 'Test Group'",
        ).fetchone()[0]
        assert groups == 0
        assert conn.execute("SELECT COUNT(*) FROM missions").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM agent_mission_status").fetchone()[0] == 0


def test_confirm_delete_group_name_requires_exact_match(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "Wrong")
    assert confirm_delete_group_name("Orientation", auto_yes=False, is_tty=True) is False

    monkeypatch.setattr("builtins.input", lambda _prompt: "Orientation")
    assert confirm_delete_group_name("Orientation", auto_yes=False, is_tty=True) is True

    assert confirm_delete_group_name("Orientation", auto_yes=True, is_tty=False) is True


def test_reject_missing_storyline(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    load_schema_only(db_path)

    with pytest.raises(StorylineDeleteError, match="not in the database"):
        delete_storyline(
            "Missing Group",
            check_only=True,
            database_path_loader=lambda: db_path,
        )


def test_write_sql_without_database_delete(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_group(db_path, pack_root)
    sql_dir = tmp_path / "sql-out"

    result = delete_storyline(
        "Test Group",
        write_sql=True,
        database_path_loader=lambda: db_path,
        sql_output_dir=sql_dir,
    )
    assert result.applied is False
    assert result.output_path == sql_dir / "test-group-delete.sql"
    assert "DELETE FROM groups" in result.output_path.read_text(encoding="utf-8")

    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM groups").fetchone()[0] == 1


def test_main_aborted_exit_code(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_group(db_path, pack_root)
    monkeypatch.setattr(
        "radspion.tools.delete_storyline.resolve_database_path",
        lambda: db_path,
    )

    with pytest.raises(SystemExit) as exc:
        main(["Test Group"])
    assert exc.value.code == 2
    assert "aborted" in capsys.readouterr().err.lower()


def test_main_rejects_check_and_write_sql(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_group(db_path, pack_root)
    monkeypatch.setattr(
        "radspion.tools.delete_storyline.resolve_database_path",
        lambda: db_path,
    )

    with pytest.raises(SystemExit) as exc:
        main(["Test Group", "--check", "--write-sql"])
    assert exc.value.code == 1
    assert "Use either --check or --write-sql" in capsys.readouterr().err


def test_reject_empty_storyline_name(tmp_path: Path):
    db_path = tmp_path / "radspion.db"
    load_schema_only(db_path)

    with pytest.raises(StorylineDeleteError, match="non-empty"):
        delete_storyline(
            "   ",
            check_only=True,
            database_path_loader=lambda: db_path,
        )


def test_format_delete_report_empty_missions(tmp_path: Path):
    db_path = tmp_path / "radspion.db"
    load_schema_only(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO groups (name) VALUES ('Empty Arc')")
        conn.commit()
        conn.row_factory = sqlite3.Row
        impact = load_delete_impact(conn, "Empty Arc")

    report = format_delete_report(impact)
    assert "Storyline: 'Empty Arc' (0 missions)" in report
    assert "Totals: 0 agent rows (0 active, 0 completed) across 0 agents" in report
