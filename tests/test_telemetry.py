from unittest.mock import patch

from app.telemetry import configure_telemetry


def test_telemetry_remains_disabled_without_connection_string(monkeypatch):
    monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)

    assert configure_telemetry() is False


def test_telemetry_uses_environment_configuration(monkeypatch):
    monkeypatch.setenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "InstrumentationKey=00000000-0000-0000-0000-000000000000",
    )

    with patch(
        "azure.monitor.opentelemetry.configure_azure_monitor"
    ) as configure_azure_monitor:
        assert configure_telemetry() is True

    configure_azure_monitor.assert_called_once_with(
        disable_logging=True,
        disable_metrics=True,
        enable_live_metrics=False,
    )
