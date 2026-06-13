"""Shared SQLite fixtures for Testing Storyline and related harnesses."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from radspion.app import create_app
from radspion.config import load_config
from radspion.database import DatabaseRadspionStorage
from radspion.radspion import Radspion
from tests.fakes.google_oauth import FakeGoogleOAuth
from tests.helpers import load_schema_only, load_testing_storyline_database


@pytest.fixture
def testing_storyline_db_path(tmp_path: Path) -> Path:
    """Path to a fresh Testing Storyline seed database."""
    db_path = tmp_path / "storyline.db"
    load_testing_storyline_database(db_path)
    return db_path


@pytest.fixture
def testing_storyline_storage(
    testing_storyline_db_path: Path,
) -> Iterator[DatabaseRadspionStorage]:
    """Seeded Testing Storyline storage; connection closed after each test."""
    storage = DatabaseRadspionStorage(testing_storyline_db_path)
    try:
        yield storage
    finally:
        storage.close()


@pytest.fixture
def testing_storyline_radspion(
    testing_storyline_storage: DatabaseRadspionStorage,
) -> Radspion:
    return Radspion(testing_storyline_storage)


@pytest.fixture
def testing_storyline_client(testing_storyline_storage: DatabaseRadspionStorage):
    """Flask test client backed by the same storage instance as testing_storyline_storage."""
    config = load_config(testing=True)
    oauth = FakeGoogleOAuth()
    radspion = Radspion(testing_storyline_storage)
    app = create_app(config=config, radspion=radspion, oauth=oauth)
    return app.test_client()


@pytest.fixture
def testing_storyline_oauth_client(testing_storyline_storage: DatabaseRadspionStorage):
    """Flask test client and OAuth fake sharing one storage instance."""
    config = load_config(testing=True)
    oauth = FakeGoogleOAuth()
    radspion = Radspion(testing_storyline_storage)
    app = create_app(config=config, radspion=radspion, oauth=oauth)
    return app.test_client(), oauth


@pytest.fixture
def schema_only_db_path(tmp_path: Path) -> Path:
    """Path to an empty schema-only database (no missions)."""
    db_path = tmp_path / "empty.db"
    load_schema_only(db_path)
    return db_path


@pytest.fixture
def schema_only_storage(schema_only_db_path: Path) -> Iterator[DatabaseRadspionStorage]:
    storage = DatabaseRadspionStorage(schema_only_db_path)
    try:
        yield storage
    finally:
        storage.close()


@pytest.fixture
def schema_only_client(schema_only_storage: DatabaseRadspionStorage):
    config = load_config(testing=True)
    oauth = FakeGoogleOAuth()
    radspion = Radspion(schema_only_storage)
    app = create_app(config=config, radspion=radspion, oauth=oauth)
    return app.test_client()
