"""Tests that storyline seeds load mission markdown into the database."""

import sqlite3


def test_orientation_seed_includes_basic_training_markdown(testing_storyline_db_path):
    with sqlite3.connect(testing_storyline_db_path) as conn:
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


def test_storyline_seed_includes_es_alpha_markdown(testing_storyline_db_path):
    with sqlite3.connect(testing_storyline_db_path) as conn:
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
