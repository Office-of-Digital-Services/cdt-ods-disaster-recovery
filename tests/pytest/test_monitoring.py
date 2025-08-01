import logging

import pytest

from web.monitoring import configure


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)


@pytest.fixture
def conn_str(monkeypatch):
    monkeypatch.setenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "InstrumentationKey=abc123")


@pytest.fixture
def mock_configure_azure_monitor(mocker):
    return mocker.patch("web.monitoring._configure_azure_monitor")


def test_configure__no_connection_string(mock_configure_azure_monitor):
    configure()

    mock_configure_azure_monitor.assert_not_called()


@pytest.mark.usefixtures("conn_str")
def test_configure__with_connection_string(mocker, mock_configure_azure_monitor):
    mock_get_logger = mocker.patch("logging.getLogger")

    configure()

    mock_configure_azure_monitor.assert_called_once()
    mock_get_logger.assert_has_calls([mocker.call("azure"), mocker.call().setLevel(logging.WARNING)])
    mock_get_logger.assert_has_calls([mocker.call("django"), mocker.call().setLevel(logging.INFO)])
    mock_get_logger.assert_has_calls([mocker.call("web"), mocker.call().setLevel("DEBUG")])


@pytest.mark.usefixtures("conn_str")
def test_configure__log_level(mocker, mock_configure_azure_monitor):
    mock_get_logger = mocker.patch("logging.getLogger")

    configure(log_level=logging.ERROR)

    mock_configure_azure_monitor.assert_called_once()
    mock_get_logger.assert_has_calls([mocker.call("web"), mocker.call().setLevel(logging.ERROR)])


@pytest.mark.usefixtures("conn_str")
def test_configure__instrumentation_options(mock_configure_azure_monitor):
    configure()

    _, kwargs = mock_configure_azure_monitor.call_args
    assert kwargs["instrumentation_options"]["fastapi"]["enabled"] is False
    assert kwargs["instrumentation_options"]["flask"]["enabled"] is False
    assert kwargs["instrumentation_options"]["psycopg2"]["enabled"] is False
