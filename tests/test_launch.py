"""Tests for launch() startup wiring."""

import pytest

from radspion.app import launch


def test_launch_returns_flask_app_with_radspion(monkeypatch, tmp_path):
    db_path = tmp_path / "radspion.db"
    monkeypatch.setenv("SECRET_KEY", "test-launch-secret")
    monkeypatch.setenv("BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    db_path.touch()

    app = launch()

    assert app.name == "radspion.app"
    assert "radspion" in app.extensions
    assert "oauth" in app.extensions


def test_launch_exits_when_secret_key_missing(monkeypatch, capsys):
    monkeypatch.setattr("radspion.app.load_dotenv", lambda: None)
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(SystemExit) as exc_info:
        launch()

    assert exc_info.value.code == 1
    assert "SECRET_KEY is required" in capsys.readouterr().err


def test_launch_exits_when_database_missing(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("SECRET_KEY", "test-launch-secret")
    missing = tmp_path / "missing" / "radspion.db"
    monkeypatch.setenv("DATABASE_PATH", str(missing))

    with pytest.raises(SystemExit) as exc_info:
        launch()

    assert exc_info.value.code == 1
    assert "Could not open database" in capsys.readouterr().err
