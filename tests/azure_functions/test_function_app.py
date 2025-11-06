import json
import pytest
import requests.exceptions

from azure_functions.function_app import (
    build_slack_message,
    fetch_search_results,
    format_alert_date,
    health_check,
    select_search_results,
    validate_function_key,
)


def test_fetch_search_results_success(mocker):
    mock_api_link = (
        "https://api.applicationinsights.io/v1/apps/mock-id/query?query=union%20%28exceptions%20%7C%20where%20type"
        "%20%21has%20%22ServiceResponseError%22%29%2C%20%28traces%20%7C%20where%20severityLevel%20%3E%3D%203%29&timespan="
        "2025-10-28T20%3a18%3a09.0000000Z%2f2025-10-28T20%3a23%3a09.0000000Z"
    )
    mock_api_key = "mock-api-key"
    mocker.patch("azure_functions.function_app.APPINSIGHTS_API_KEY", mock_api_key)
    mock_api_response = {
        "tables": [
            {
                "name": "PrimaryResult",
                "columns": [
                    {"name": "timestamp", "type": "datetime"},
                    {"name": "problemId", "type": "string"},
                    {"name": "outerMessage", "type": "string"},
                ],
                "rows": [
                    [
                        "2025-10-28T20:21:04.1465456Z",
                        "",
                        "System.Private.CoreLib, Version=8.0.0.0, Culture=neutral, " "PublicKeyToken=7cec85d7bea7798e",
                        "System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw",
                    ]
                ],
            }
        ]
    }
    expected_table_result = mock_api_response["tables"][0]
    expected_headers = {"x-api-key": mock_api_key}
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = mock_api_response
    mock_response.raise_for_status.return_value = None
    mock_requests_get = mocker.patch("azure_functions.function_app.requests.get", return_value=mock_response)

    search_results = fetch_search_results(mock_api_link)

    mock_requests_get.assert_called_once_with(mock_api_link, headers=expected_headers)
    mock_response.raise_for_status.assert_called_once()
    mock_response.json.assert_called_once()
    assert search_results == expected_table_result


def test_fetch_search_results_error(mocker):
    mock_api_link = (
        "https://api.applicationinsights.io/v1/apps/mock-id/query?query=union%20%28exceptions%20%7C%20where%20type"
        "%20%21has%20%22ServiceResponseError%22%29%2C%20%28traces%20%7C%20where%20severityLevel%20%3E%3D%203%29&timespan="
        "2025-10-28T20%3a18%3a09.0000000Z%2f2025-10-28T20%3a23%3a09.0000000Z"
    )
    mock_api_key = "mock-api-key"
    mocker.patch("azure_functions.function_app.APPINSIGHTS_API_KEY", mock_api_key)
    test_exception = requests.exceptions.RequestException("Connection error")
    mock_requests_get = mocker.patch("azure_functions.function_app.requests.get", side_effect=test_exception)

    expected_headers = {"x-api-key": mock_api_key}
    expected_error_result = {"error": "Failed to fetch log details."}

    search_results = fetch_search_results(mock_api_link)

    mock_requests_get.assert_called_once_with(mock_api_link, headers=expected_headers)
    assert search_results == expected_error_result


def test_select_search_results(log_search_result):
    """Test the selection logic."""
    result = select_search_results(log_search_result)
    expected = {
        "problemId": "pid-123",
        "outerMessage": "Error msg",
        "details": "JSON details",
        "client_City": "TestCity",
        "client_StateOrProvince": "TestState",
        "cloud_RoleInstance": "Instance-1",
    }
    assert result == expected


@pytest.mark.parametrize(
    "data, expected_output",
    [("2023-01-01T12:00:00.12345Z", "2023-01-01T12:00:00Z"), ("", "N/A"), (None, "N/A"), ("invalid-datetime", "N/A")],
)
def test_format_alert_date(data, expected_output):
    result = format_alert_date(data)
    assert result == expected_output


@pytest.fixture
def saved_function_key(mocker):
    function_key = "saved_key"
    mocker.patch("azure_functions.function_app.FUNCTION_KEY", function_key)


@pytest.mark.parametrize(
    "received_function_key, expected_return",
    [
        ("saved_key", None),
        ("wrong_key", ("Unauthorized: invalid code.", 403)),
        (None, ("Missing code authentication.", 401)),
    ],
)
@pytest.mark.usefixtures("saved_function_key")
def test_validate_function_key(received_function_key, expected_return, mock_http_response):
    result = validate_function_key(received_function_key)
    assert result == expected_return


@pytest.fixture
def sample_alert_data():
    """Provides sample test alert data"""
    return {
        "essentials": {
            "alertId": "alert-id-001",
            "alertRule": "msqalert-cdt-pub-vip-ddrc-T-001",
            "severity": "Sev1",
            "firedDateTime": "2023-01-01T12:00:00.12345Z",
            "investigationLink": "http://link.to/portal",
        },
        "alertContext": {"condition": {"allOf": [{"linkToSearchResultsAPI": "http://link.to/api"}]}},
    }


@pytest.fixture
def sample_alert_prod_data(sample_alert_data):
    """Provides sample production alert data"""
    sample_alert_data["essentials"]["alertRule"] = "msqalert-cdt-pub-vip-ddrc-P-001"
    return sample_alert_data


@pytest.mark.parametrize(
    "data, expected_heading",
    [
        ("sample_alert_data", "*Azure Alert Fired: msqalert-cdt-pub-vip-ddrc-T-001*"),
        ("sample_alert_prod_data", "🚨 *Azure Alert Fired: msqalert-cdt-pub-vip-ddrc-P-001*"),
    ],
)
def test_build_slack_message(data, expected_heading, mocker, request):
    data = request.getfixturevalue(data)
    mocker.patch("azure_functions.function_app.PRODUCTION_ALERT_RULE", "msqalert-cdt-pub-vip-ddrc-P-001")
    mocker.patch(
        "azure_functions.function_app.fetch_search_results",
        return_value={"tables": [], "rows": []},
    )
    mocker.patch(
        "azure_functions.function_app.select_search_results",
        return_value={"problemId": "mocked-id", "outerMessage": "mocked error"},
    )
    message = build_slack_message(data)

    assert expected_heading in message
    assert "*Severity*: Sev1" in message
    assert "*Date*: 2023-01-01T12:00:00Z" in message
    assert "*Alert ID*: alert-id-001" in message
    assert "*problemId:* mocked-id" in message
    assert "*outerMessage:* mocked error" in message
    assert "<http://link.to/portal|Click here to investigate in Azure Portal>" in message


@pytest.mark.usefixtures("mock_http_response")
def test_health_check(mocker):
    """
    Test the health_check endpoint.
    """
    mock_req = mocker.MagicMock()

    response = health_check(mock_req)

    assert response == ("Healthy.", 200)
