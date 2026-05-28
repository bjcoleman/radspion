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
