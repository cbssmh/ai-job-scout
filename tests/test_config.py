import pytest

from app import config
from app.config import load_settings


def test_provider_analysis_defaults_to_disabled(monkeypatch):
    monkeypatch.delenv("PROVIDER_ANALYSIS_ENABLED", raising=False)

    assert load_settings().provider_analysis_enabled is False


def test_disabled_settings_do_not_read_provider_credentials(monkeypatch):
    credential_names = {"NVIDIA_API_KEY", "OPENAI_API_KEY"}

    def guarded_getenv(name, default=None):
        if name == "PROVIDER_ANALYSIS_ENABLED":
            return "false"
        if name in credential_names:
            raise AssertionError(f"credential accessed: {name}")
        return default

    monkeypatch.setattr(config.os, "getenv", guarded_getenv)

    loaded = load_settings()

    assert loaded.provider_analysis_enabled is False
    assert loaded.nvidia_api_key is None
    assert loaded.openai_api_key is None


@pytest.mark.parametrize("value", ["true", "1", "yes", "on", " TRUE "])
def test_provider_analysis_can_be_enabled_explicitly(monkeypatch, value):
    monkeypatch.setenv("PROVIDER_ANALYSIS_ENABLED", value)

    assert load_settings().provider_analysis_enabled is True


@pytest.mark.parametrize("value", ["false", "0", "no", "off", " FALSE "])
def test_provider_analysis_can_be_disabled_explicitly(monkeypatch, value):
    monkeypatch.setenv("PROVIDER_ANALYSIS_ENABLED", value)

    assert load_settings().provider_analysis_enabled is False


def test_invalid_provider_analysis_setting_fails_fast(monkeypatch):
    monkeypatch.setenv("PROVIDER_ANALYSIS_ENABLED", "sometimes")

    with pytest.raises(ValueError, match="PROVIDER_ANALYSIS_ENABLED must be one of"):
        load_settings()
