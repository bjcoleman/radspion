"""Shared pytest fixtures."""

import pytest

from radspion.app import create_app
from radspion.config import load_config
from radspion.radspion import Radspion
from tests.fakes.storage import InMemoryRadspionStorage


@pytest.fixture
def config():
    return load_config(testing=True)


@pytest.fixture
def storage():
    """In-memory storage with no registration codes."""
    return InMemoryRadspionStorage()


@pytest.fixture
def radspion(storage):
    return Radspion(storage)


@pytest.fixture
def app(config, radspion):
    return create_app(config=config, radspion=radspion)


@pytest.fixture
def client(app):
    return app.test_client()
