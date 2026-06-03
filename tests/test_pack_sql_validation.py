"""Tests for storyline pack SQL validation."""

from pathlib import Path

import pytest

from radspion.pack_sql_validation import PackValidationError, validate_pack_sql
from tests.helpers import SQL_DIR, execute_sql_file, load_testing_storyline_database

OVERLAP_PACK_SQL = """
PRAGMA foreign_keys = ON;
BEGIN;
INSERT INTO groups (name) VALUES ('Overlap Pack');
INSERT INTO missions (
    slug, title, brief_markdown, debrief_markdown, group_id, access_rule, completion_code
) VALUES (
    'overlap-mission',
    'Overlap Mission',
    'brief',
    'debrief',
    (SELECT id FROM groups WHERE name = 'Overlap Pack'),
    'unlock_code',
    'SHARED-CODE'
);
INSERT INTO mission_unlock_codes (mission_id, unlock_code)
SELECT id, 'SHARED-CODE' FROM missions WHERE slug = 'overlap-mission';
COMMIT;
"""

DUPLICATE_COMPLETION_PACK_SQL = """
PRAGMA foreign_keys = ON;
BEGIN;
INSERT INTO groups (name) VALUES ('Duplicate Pack');
INSERT INTO missions (
    slug, title, brief_markdown, debrief_markdown, group_id, access_rule, completion_code
) VALUES
    (
        'dup-a',
        'Dup A',
        'brief',
        'debrief',
        (SELECT id FROM groups WHERE name = 'Duplicate Pack'),
        'open',
        'SAME-COMPLETION'
    ),
    (
        'dup-b',
        'Dup B',
        'brief',
        'debrief',
        (SELECT id FROM groups WHERE name = 'Duplicate Pack'),
        'open',
        'SAME-COMPLETION'
    );
COMMIT;
"""


@pytest.fixture
def schema_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "schema.db"
    with __import__("sqlite3").connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        execute_sql_file(conn, SQL_DIR / "schema.sql")
        conn.commit()
    return db_path


def test_validate_accepts_testing_storyline_seed(schema_db: Path, tmp_path: Path) -> None:
    pack_sql = tmp_path / "testing.sql"
    pack_sql.write_text((SQL_DIR / "seed_testing_storyline.sql").read_text(encoding="utf-8"))

    validate_pack_sql(pack_sql, schema_db, schema_path=SQL_DIR / "schema.sql")


def test_validate_rejects_internal_unlock_completion_overlap(
    schema_db: Path,
    tmp_path: Path,
) -> None:
    pack_sql = tmp_path / "overlap.sql"
    pack_sql.write_text(OVERLAP_PACK_SQL, encoding="utf-8")

    with pytest.raises(PackValidationError, match="both listing and completion"):
        validate_pack_sql(pack_sql, schema_db, schema_path=SQL_DIR / "schema.sql")


def test_validate_rejects_duplicate_completion_codes(
    schema_db: Path,
    tmp_path: Path,
) -> None:
    pack_sql = tmp_path / "duplicate.sql"
    pack_sql.write_text(DUPLICATE_COMPLETION_PACK_SQL, encoding="utf-8")

    with pytest.raises(PackValidationError, match="duplicate completion data"):
        validate_pack_sql(pack_sql, schema_db, schema_path=SQL_DIR / "schema.sql")


def test_validate_rejects_overlap_with_existing_database(tmp_path: Path) -> None:
    db_path = tmp_path / "storyline.db"
    load_testing_storyline_database(db_path)

    pack_sql = tmp_path / "conflict.sql"
    pack_sql.write_text(
        """
PRAGMA foreign_keys = ON;
BEGIN;
INSERT INTO groups (name) VALUES ('Conflict Pack');
INSERT INTO missions (
    slug, title, brief_markdown, debrief_markdown, group_id, access_rule, completion_code
) VALUES (
    'conflict-mission',
    'Conflict Mission',
    'brief',
    'debrief',
    (SELECT id FROM groups WHERE name = 'Conflict Pack'),
    'unlock_code',
    'NEW-COMPLETION'
);
INSERT INTO mission_unlock_codes (mission_id, unlock_code)
SELECT id, 'COMPLETE es-alpha' FROM missions WHERE slug = 'conflict-mission';
COMMIT;
""",
        encoding="utf-8",
    )

    with pytest.raises(PackValidationError, match="conflict with the database"):
        validate_pack_sql(pack_sql, db_path, schema_path=SQL_DIR / "schema.sql")
