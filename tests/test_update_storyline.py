"""Tests for storyline content updates and update_storyline CLI."""

from __future__ import annotations

import shutil
import sqlite3
from dataclasses import replace
from pathlib import Path

import pytest

from radspion.storyline_pack import StorylineError, StorylinePack, load_pack
from radspion.storyline_update import (
    StorylineUpdateAborted,
    StorylineUpdateError,
    apply_update_sql,
    confirm_sensitive_changes,
    diff_pack_against_db,
    format_diff_report,
    generate_update_sql,
    load_db_state,
    verify_pack_structure,
)
from radspion.tools.seed_storyline import seed_storyline
from radspion.tools.update_storyline import main, update_storyline
from tests.helpers import load_schema_only, write_minimal_pack


def _write_requires_complete_pack(pack_root: Path) -> None:
    pack_root.mkdir(parents=True, exist_ok=True)
    (pack_root / "storyline.yaml").write_text(
        """group: Test Group
missions:
  - slug: alpha
    title: Alpha
    access: open
    completion_data: ALPHA-DATA
  - slug: bravo
    title: Bravo
    access:
      requires_complete:
        - alpha
    completion_data: BRAVO-DATA
""",
        encoding="utf-8",
    )
    for slug in ("alpha", "bravo"):
        mission_dir = pack_root / slug
        mission_dir.mkdir(exist_ok=True)
        (mission_dir / "brief.md").write_text(f"## Brief {slug}\n", encoding="utf-8")
        (mission_dir / "debrief.md").write_text(f"## Debrief {slug}\n", encoding="utf-8")


def _write_clearance_pack(pack_root: Path) -> None:
    pack_root.mkdir(parents=True, exist_ok=True)
    (pack_root / "storyline.yaml").write_text(
        """group: Test Group
missions:
  - slug: alpha
    title: Alpha
    access: open
    completion_data: ALPHA-DATA
  - slug: bravo
    title: Bravo
    access:
      clearance_code: "CODE-ONE"
    completion_data: BRAVO-DATA
""",
        encoding="utf-8",
    )
    for slug in ("alpha", "bravo"):
        mission_dir = pack_root / slug
        mission_dir.mkdir(exist_ok=True)
        (mission_dir / "brief.md").write_text(f"## Brief {slug}\n", encoding="utf-8")
        (mission_dir / "debrief.md").write_text(f"## Debrief {slug}\n", encoding="utf-8")


def _seed_pack(db_path: Path, pack_root: Path) -> None:
    load_schema_only(db_path)
    seed_storyline(pack_root, database_path_loader=lambda: db_path)


def _read_title(db_path: Path, slug: str) -> str:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT title FROM missions WHERE slug = ?",
            (slug,),
        ).fetchone()
    assert row is not None
    return row[0]


def test_check_reports_no_changes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)
    monkeypatch.setattr(
        "radspion.tools.update_storyline.resolve_database_path",
        lambda: db_path,
    )

    with pytest.raises(SystemExit) as exc:
        main([str(pack_root), "--check"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "no content changes" in captured.out


def test_apply_updates_brief_without_prompt(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "alpha" / "brief.md").write_text("## Brief\n\nUpdated copy.\n", encoding="utf-8")

    result = update_storyline(
        pack_root,
        is_tty=False,
        database_path_loader=lambda: db_path,
    )
    assert result.applied is True

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT brief_markdown FROM missions WHERE slug = 'alpha'",
        ).fetchone()
    assert "Updated copy." in row[0]


def test_completion_data_blocked_without_yes(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "storyline.yaml").write_text(
        """group: Test Group
missions:
  - slug: alpha
    title: Alpha
    access: open
    completion_data: NEW-DATA
""",
        encoding="utf-8",
    )

    with pytest.raises(StorylineUpdateAborted):
        update_storyline(
            pack_root,
            is_tty=False,
            database_path_loader=lambda: db_path,
        )

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT completion_data FROM missions WHERE slug = 'alpha'",
        ).fetchone()
    assert row[0] == "ALPHA-DATA"


def test_completion_data_applied_with_yes(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "storyline.yaml").write_text(
        """group: Test Group
missions:
  - slug: alpha
    title: Alpha
    access: open
    completion_data: NEW-DATA
""",
        encoding="utf-8",
    )

    result = update_storyline(
        pack_root,
        auto_yes=True,
        database_path_loader=lambda: db_path,
    )
    assert result.applied is True

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT completion_data FROM missions WHERE slug = 'alpha'",
        ).fetchone()
    assert row[0] == "NEW-DATA"


def test_clearance_code_blocked_without_yes(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    _write_clearance_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    storyline = (pack_root / "storyline.yaml").read_text(encoding="utf-8")
    (pack_root / "storyline.yaml").write_text(
        storyline.replace("CODE-ONE", "CODE-TWO"),
        encoding="utf-8",
    )

    with pytest.raises(StorylineUpdateAborted):
        update_storyline(
            pack_root,
            is_tty=False,
            database_path_loader=lambda: db_path,
        )

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT mcc.clearance_code
            FROM mission_clearance_codes mcc
            JOIN missions m ON m.id = mcc.mission_id
            WHERE m.slug = 'bravo'
            """,
        ).fetchone()
    assert row[0] == "CODE-ONE"


def test_sensitive_update_is_all_or_nothing(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "alpha" / "brief.md").write_text("## Brief\n\nUpdated copy.\n", encoding="utf-8")
    (pack_root / "storyline.yaml").write_text(
        """group: Test Group
missions:
  - slug: alpha
    title: Alpha
    access: open
    completion_data: NEW-DATA
""",
        encoding="utf-8",
    )

    with pytest.raises(StorylineUpdateAborted):
        update_storyline(
            pack_root,
            is_tty=False,
            database_path_loader=lambda: db_path,
        )

    with sqlite3.connect(db_path) as conn:
        brief = conn.execute(
            "SELECT brief_markdown FROM missions WHERE slug = 'alpha'",
        ).fetchone()[0]
        completion = conn.execute(
            "SELECT completion_data FROM missions WHERE slug = 'alpha'",
        ).fetchone()[0]
    assert "Updated copy." not in brief
    assert completion == "ALPHA-DATA"


def test_reject_access_rule_change(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "storyline.yaml").write_text(
        """group: Test Group
missions:
  - slug: alpha
    title: Alpha
    access:
      clearance_code: "NEW-CODE"
    completion_data: ALPHA-DATA
""",
        encoding="utf-8",
    )

    with pytest.raises(StorylineUpdateError, match="access_rule mismatch"):
        update_storyline(
            pack_root,
            database_path_loader=lambda: db_path,
        )


def test_reject_missing_database_group(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    load_schema_only(db_path)

    with pytest.raises(StorylineUpdateError, match="not in the database"):
        update_storyline(
            pack_root,
            check_only=True,
            database_path_loader=lambda: db_path,
        )


def test_reject_extra_database_mission(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    _write_clearance_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "storyline.yaml").write_text(
        """group: Test Group
missions:
  - slug: alpha
    title: Alpha
    access: open
    completion_data: ALPHA-DATA
""",
        encoding="utf-8",
    )
    shutil.rmtree(pack_root / "bravo")

    with pytest.raises(StorylineUpdateError, match="Mission set mismatch"):
        update_storyline(
            pack_root,
            check_only=True,
            database_path_loader=lambda: db_path,
        )


def test_write_sql_without_database_write(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "alpha" / "brief.md").write_text("## Brief\n\nUpdated copy.\n", encoding="utf-8")

    result = update_storyline(
        pack_root,
        write_sql=True,
        database_path_loader=lambda: db_path,
    )
    assert result.applied is False
    assert result.output_path == pack_root / "test-pack-update.sql"
    sql = result.output_path.read_text(encoding="utf-8")
    assert "UPDATE missions" in sql
    assert "Updated copy." in sql

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT brief_markdown FROM missions WHERE slug = 'alpha'",
        ).fetchone()
    assert "Updated copy." not in row[0]


def test_main_aborted_exit_code(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)
    monkeypatch.setattr(
        "radspion.tools.update_storyline.resolve_database_path",
        lambda: db_path,
    )

    (pack_root / "storyline.yaml").write_text(
        """group: Test Group
missions:
  - slug: alpha
    title: Alpha
    access: open
    completion_data: NEW-DATA
""",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as exc:
        main([str(pack_root)])
    assert exc.value.code == 2
    assert "aborted" in capsys.readouterr().err.lower()


def test_generate_update_sql_includes_clearance(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    _write_clearance_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    storyline = (pack_root / "storyline.yaml").read_text(encoding="utf-8")
    (pack_root / "storyline.yaml").write_text(
        storyline.replace("CODE-ONE", "CODE-TWO"),
        encoding="utf-8",
    )

    pack = load_pack(pack_root)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        db_state = load_db_state(conn, pack.group)
    verify_pack_structure(pack, db_state)
    diff = diff_pack_against_db(pack, db_state)
    sql = generate_update_sql(pack, diff, db_state)
    assert "UPDATE mission_clearance_codes" in sql
    assert "CODE-TWO" in sql


def test_apply_title_change(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "storyline.yaml").write_text(
        """group: Test Group
missions:
  - slug: alpha
    title: Alpha Updated
    access: open
    completion_data: ALPHA-DATA
""",
        encoding="utf-8",
    )

    update_storyline(
        pack_root,
        database_path_loader=lambda: db_path,
    )
    assert _read_title(db_path, "alpha") == "Alpha Updated"


def test_diff_report_lists_sensitive_and_changed_fields(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    _write_clearance_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "alpha" / "debrief.md").write_text("## Debrief\n\nNew ending.\n", encoding="utf-8")
    storyline = (pack_root / "storyline.yaml").read_text(encoding="utf-8")
    storyline = storyline.replace("CODE-ONE", "CODE-TWO")
    storyline = storyline.replace("title: Alpha", "title: Alpha Retitled")
    storyline = storyline.replace("completion_data: ALPHA-DATA", "completion_data: NEW-ALPHA-DATA")
    (pack_root / "storyline.yaml").write_text(storyline, encoding="utf-8")

    pack = load_pack(pack_root)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        db_state = load_db_state(conn, pack.group)
    diff = diff_pack_against_db(pack, db_state)

    report = format_diff_report(diff)
    assert "1 title" in report
    assert "1 debrief" in report
    assert "1 clearance_code" in report
    assert "1 completion_data" in report
    assert "Sensitive changes: clearance_code, completion_data" in report
    assert "CODE-ONE' → 'CODE-TWO'" in report
    assert diff.changed_mission_slugs() == ["alpha", "bravo"]
    assert diff.sensitive_mission_slugs() == ["alpha", "bravo"]


def test_format_diff_report_counts_brief_only(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "alpha" / "brief.md").write_text(
        "## Brief\n\nOnly the brief changed.\n",
        encoding="utf-8",
    )
    pack = load_pack(pack_root)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        db_state = load_db_state(conn, pack.group)
    diff = diff_pack_against_db(pack, db_state)

    report = format_diff_report(diff)
    assert "1 brief would change" in report
    assert "Sensitive changes" not in report


def test_load_db_state_reads_requires_complete_edges(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    _write_requires_complete_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        db_state = load_db_state(conn, "Test Group")

    assert db_state.missions["bravo"].requires_complete == frozenset({"alpha"})


def test_load_db_state_rejects_missing_clearance_row(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    _write_clearance_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            DELETE FROM mission_clearance_codes
            WHERE mission_id = (SELECT id FROM missions WHERE slug = 'bravo')
            """,
        )
        conn.commit()
        conn.row_factory = sqlite3.Row
        with pytest.raises(StorylineUpdateError, match="no clearance row"):
            load_db_state(conn, "Test Group")


def test_load_db_state_rejects_orphan_clearance_row(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    _write_clearance_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    with sqlite3.connect(db_path) as conn:
        alpha_id = conn.execute(
            "SELECT id FROM missions WHERE slug = 'alpha'",
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO mission_clearance_codes (mission_id, clearance_code) VALUES (?, ?)",
            (alpha_id, "ORPHAN-CODE"),
        )
        conn.commit()
        conn.row_factory = sqlite3.Row
        with pytest.raises(StorylineUpdateError, match="access_rule is not clearance_code"):
            load_db_state(conn, "Test Group")


def test_reject_group_name_mismatch(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    pack = load_pack(pack_root)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        db_state = load_db_state(conn, pack.group)
    mismatched_pack = StorylinePack(
        root=pack.root,
        group="Other Group",
        missions=pack.missions,
    )

    with pytest.raises(StorylineUpdateError, match="Group name mismatch"):
        verify_pack_structure(mismatched_pack, db_state)


def test_reject_pack_mission_missing_from_database(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    charlie_dir = pack_root / "charlie"
    charlie_dir.mkdir()
    (charlie_dir / "brief.md").write_text("## Brief\n", encoding="utf-8")
    (charlie_dir / "debrief.md").write_text("## Debrief\n", encoding="utf-8")
    (pack_root / "storyline.yaml").write_text(
        """group: Test Group
missions:
  - slug: alpha
    title: Alpha
    access: open
    completion_data: ALPHA-DATA
  - slug: charlie
    title: Charlie
    access: open
    completion_data: CHARLIE-DATA
""",
        encoding="utf-8",
    )

    with pytest.raises(StorylineUpdateError, match="pack missions missing from database"):
        update_storyline(
            pack_root,
            check_only=True,
            database_path_loader=lambda: db_path,
        )


def test_reject_requires_complete_mismatch(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    _write_requires_complete_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    pack = load_pack(pack_root)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        db_state = load_db_state(conn, pack.group)
    corrupted_bravo = replace(db_state.missions["bravo"], requires_complete=frozenset())
    corrupted_state = replace(
        db_state,
        missions={**db_state.missions, "bravo": corrupted_bravo},
    )

    with pytest.raises(StorylineUpdateError, match="requires_complete mismatch"):
        verify_pack_structure(pack, corrupted_state)


def test_generate_update_sql_for_debrief_only(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    (pack_root / "alpha" / "debrief.md").write_text("## Debrief\n\nNew ending.\n", encoding="utf-8")
    pack = load_pack(pack_root)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        db_state = load_db_state(conn, pack.group)
    diff = diff_pack_against_db(pack, db_state)
    sql = generate_update_sql(pack, diff, db_state)
    assert "debrief_markdown" in sql
    assert "New ending." in sql


def test_generate_update_sql_returns_empty_when_no_changes(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    pack = load_pack(pack_root)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        db_state = load_db_state(conn, pack.group)
    diff = diff_pack_against_db(pack, db_state)
    assert generate_update_sql(pack, diff, db_state) == ""


def test_apply_update_sql_noop_on_empty_script(tmp_path: Path):
    db_path = tmp_path / "radspion.db"
    load_schema_only(db_path)
    with sqlite3.connect(db_path) as conn:
        apply_update_sql(conn, "   ")
        assert conn.execute("SELECT COUNT(*) FROM groups").fetchone()[0] == 0


def test_verify_pack_structure_rejects_invalid_clearance_pack(tmp_path: Path):
    pack_root = tmp_path / "test-pack"
    _write_clearance_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)

    pack = load_pack(pack_root)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        db_state = load_db_state(conn, pack.group)

    bravo = next(mission for mission in pack.missions if mission.slug == "bravo")
    broken_mission = replace(bravo, clearance_code=None)
    broken_pack = StorylinePack(
        root=pack.root,
        group=pack.group,
        missions=tuple(
            broken_mission if mission.slug == "bravo" else mission for mission in pack.missions
        ),
    )
    with pytest.raises(StorylineError, match="missing clearance_code"):
        verify_pack_structure(broken_pack, db_state)

    alpha = next(mission for mission in pack.missions if mission.slug == "alpha")
    stray_clearance = replace(alpha, clearance_code="STRAY-CODE")
    stray_pack = StorylinePack(
        root=pack.root,
        group=pack.group,
        missions=tuple(
            stray_clearance if mission.slug == "alpha" else mission for mission in pack.missions
        ),
    )
    with pytest.raises(StorylineError, match="unexpected clearance_code"):
        verify_pack_structure(stray_pack, db_state)


def test_confirm_sensitive_changes_tty_paths(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "y")
    assert confirm_sensitive_changes(auto_yes=False, is_tty=True) is True

    monkeypatch.setattr("builtins.input", lambda _prompt: "n")
    assert confirm_sensitive_changes(auto_yes=False, is_tty=True) is False

    assert confirm_sensitive_changes(auto_yes=True, is_tty=False) is True
    assert confirm_sensitive_changes(auto_yes=False, is_tty=False) is False


def test_main_rejects_check_and_write_sql(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
):
    pack_root = tmp_path / "test-pack"
    write_minimal_pack(pack_root)
    db_path = tmp_path / "radspion.db"
    _seed_pack(db_path, pack_root)
    monkeypatch.setattr(
        "radspion.tools.update_storyline.resolve_database_path",
        lambda: db_path,
    )

    with pytest.raises(SystemExit) as exc:
        main([str(pack_root), "--check", "--write-sql"])
    assert exc.value.code == 1
    assert "Use either --check or --write-sql" in capsys.readouterr().err
