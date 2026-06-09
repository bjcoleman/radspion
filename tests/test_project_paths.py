"""Tests for repository path resolution."""

from pathlib import Path

from radspion import project_paths
from radspion.project_paths import database_path, project_root, schema_path


def test_project_root_contains_expected_layout():
    root = project_root()
    assert (root / "pyproject.toml").is_file()
    assert (root / "src" / "radspion").is_dir()


def test_schema_and_testing_seed_paths():
    assert schema_path().name == "schema.sql"
    assert schema_path().is_file()
    assert project_paths.testing_seed_path().name == "seed_testing_storyline.sql"
    assert project_paths.testing_seed_path().is_file()


def test_database_path_default(monkeypatch):
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    path = database_path()
    assert path.name == "radspion.db"
    assert path.parent.name == "database"
    assert path.is_absolute()


def test_database_path_respects_env(monkeypatch, tmp_path: Path):
    custom = tmp_path / "custom.db"
    monkeypatch.setenv("DATABASE_PATH", str(custom))
    assert database_path() == custom.resolve()
