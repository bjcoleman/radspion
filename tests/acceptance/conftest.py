"""Fixtures for browser acceptance tests (live Flask server + Playwright)."""

from __future__ import annotations

import socket
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

import pytest
from tests.fakes.google_oauth import FakeGoogleOAuth
from tests.helpers import SAMPLE_AGENTS, load_testing_storyline_database
from werkzeug.serving import make_server

from radspion.app import create_app
from radspion.config import load_config
from radspion.database import DatabaseRadspionStorage
from radspion.radspion import Radspion

_OAUTH_CALLBACK_CODE = "test-code"
_OAUTH_CALLBACK_STATE = "test-oauth-state"


@dataclass(frozen=True)
class LiveApp:
    """Running Flask app for acceptance tests."""

    base_url: str
    oauth: FakeGoogleOAuth
    database_path: Path


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Skip transmission modal progress animations (~3s each)."""
    return {**browser_context_args, "reduced_motion": "reduce"}


@pytest.fixture
def testing_storyline_db(tmp_path: Path) -> Path:
    """Fresh Testing Storyline seed for each acceptance test."""
    db_path = tmp_path / "storyline.db"
    load_testing_storyline_database(db_path)
    return db_path


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_server(base_url: str, *, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/") as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.05)
    raise RuntimeError(f"Server at {base_url} did not become ready within {timeout}s")


@pytest.fixture
def live_app(testing_storyline_db: Path) -> LiveApp:
    """Start Flask on a random port with a seeded SQLite database."""
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    config = replace(
        load_config(testing=True),
        database_path=testing_storyline_db,
        base_url=base_url,
    )
    oauth = FakeGoogleOAuth()
    oauth.redirect_uri = f"{base_url}/auth/google/callback"
    storage = DatabaseRadspionStorage(config.database_path)
    radspion = Radspion(storage)
    app = create_app(config=config, radspion=radspion, oauth=oauth)

    server = make_server("127.0.0.1", port, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    _wait_for_server(base_url)

    yield LiveApp(base_url=base_url, oauth=oauth, database_path=testing_storyline_db)

    server.shutdown()
    storage.close()


@pytest.fixture
def login_as(live_app: LiveApp, page) -> Callable[[str], None]:
    """Sign in as a sample agent from the Testing Storyline seed via fake OAuth."""

    def _login(agent_key: str) -> None:
        agent = SAMPLE_AGENTS[agent_key]
        live_app.oauth.returns(
            google_subject_id=agent["google_subject_id"],
            email=agent["email"],
            display_name=agent["display_name"],
        )
        page.request.get(f"{live_app.base_url}/auth/google", max_redirects=0)
        page.request.get(
            f"{live_app.base_url}/auth/google/callback"
            f"?code={_OAUTH_CALLBACK_CODE}&state={_OAUTH_CALLBACK_STATE}",
            max_redirects=0,
        )

    return _login
