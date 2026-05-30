"""Tests for configuration loading."""

import pytest

from radspion.config import ConfigurationError, load_config


def test_load_config_requires_secret_key_when_not_testing(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(ConfigurationError, match="SECRET_KEY is required"):
        load_config(testing=False)


def test_load_config_uses_test_secret_when_testing(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    config = load_config(testing=True)

    assert config.testing is True
    assert config.secret_key
    assert config.base_url == "http://localhost:8000"
    assert config.google_client_id
    assert config.google_client_secret


def test_load_config_requires_oauth_settings_when_not_testing(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "prod-secret")
    monkeypatch.delenv("BASE_URL", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)

    with pytest.raises(ConfigurationError, match="BASE_URL is required"):
        load_config(testing=False)


def test_load_config_requires_google_client_id(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "prod-secret")
    monkeypatch.setenv("BASE_URL", "http://localhost:8000")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)

    with pytest.raises(ConfigurationError, match="GOOGLE_CLIENT_ID is required"):
        load_config(testing=False)


def test_load_config_requires_google_client_secret(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "prod-secret")
    monkeypatch.setenv("BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "prod-google-client-id")
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)

    with pytest.raises(ConfigurationError, match="GOOGLE_CLIENT_SECRET is required"):
        load_config(testing=False)
