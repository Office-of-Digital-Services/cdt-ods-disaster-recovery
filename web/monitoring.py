import logging
import os

from azure.monitor.opentelemetry import configure_azure_monitor as _configure_azure_monitor
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor


def configure(log_level: str = "DEBUG"):
    """Configure application error monitoring with Azure Application Insights.

    Requires the `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable to have a valid connection string.
    """
    connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if connection_string:
        # configure Tracing
        _configure_azure_monitor(
            connection_string=connection_string,
            # turn off bundled instrumentations that are unused here
            instrumentation_options={
                "fastapi": {"enabled": False},
                "flask": {"enabled": False},
                "psycopg2": {"enabled": False},
            },
        )

        # Manually instrument psycopg v3
        PsycopgInstrumentor().instrument()

        # override log levels for some loggers
        logger_levels = {"azure": logging.WARNING, "django": logging.INFO, "web": log_level}
        for logger_name, level in logger_levels.items():
            logging.getLogger(logger_name).setLevel(level)
