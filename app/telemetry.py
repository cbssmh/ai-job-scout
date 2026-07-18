import os


def configure_telemetry() -> bool:
    """Enable Azure Monitor tracing when the runtime is configured for it."""
    if not os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        return False

    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor(
        disable_logging=True,
        disable_metrics=True,
        enable_live_metrics=False,
    )
    return True
