"""Tests that storyline seeds load mission markdown into the database."""

import sqlite3
from pathlib import Path

import pytest

from tests.helpers import load_orientation_database, load_testing_storyline_database


@pytest.fixture
def orientation_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "orientation.db"
    load_orientation_database(db_path)
    return db_path


@pytest.fixture
def storyline_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "storyline.db"
    load_testing_storyline_database(db_path)
    return db_path


def test_orientation_seed_includes_basic_training_markdown(orientation_db: Path):
    with sqlite3.connect(orientation_db) as conn:
        row = conn.execute(
            """
            SELECT brief_markdown, debrief_markdown
            FROM missions
            WHERE slug = 'basic-training'
            """,
        ).fetchone()
    assert row is not None
    assert "Welcome to Radspion" in row[0]
    assert "Placeholder. Shown after completion only." in row[1]


def test_storyline_seed_includes_es_alpha_markdown(storyline_db: Path):
    with sqlite3.connect(storyline_db) as conn:
        row = conn.execute(
            """
            SELECT brief_markdown, debrief_markdown
            FROM missions
            WHERE slug = 'es-alpha'
            """,
        ).fetchone()
    assert row is not None
    assert "ES: Alpha" in row[0]
    assert "ES: Gamma" in row[1]
