import json
import textwrap
import pytest
import requests.exceptions

import azure.functions as func
from azure_functions.function_app import (
    alert_to_slack,
    build_slack_message,
    fetch_search_results,
    format_alert_date,
    format_search_results,
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


def test_format_search_results_empty():
    """An empty details item."""
    data = {}
    expected_result = "_No additional details found._\n"
    result = format_search_results(data)
    assert result == expected_result


def test_format_search_results_simple():
    """details contains simple key-value pairs."""
    data = {"problemId": "pid-123", "outerMessage": "Error msg"}
    expected_result = "*problemId:* pid-123\n*outerMessage:* Error msg\n"
    result = format_search_results(data)
    assert result == expected_result


def test_format_search_results_details_not_json():
    """details is a plain string, not JSON."""
    data = {"details": "This is just a string."}
    expected_result = "*details:* This is just a string.\n"
    result = format_search_results(data)
    assert result == expected_result


def test_format_search_results_details_json_not_list():
    """details is valid JSON, but not a list."""
    data = {"details": json.dumps({"key": "value"})}
    expected_result = "*details:* {'key': 'value'}\n"
    result = format_search_results(data)
    assert result == expected_result


def test_format_search_results_details_with_short_raw_stack():
    """details contains a JSON list with a short rawStack."""
    short_stack = textwrap.dedent(
        """
        Traceback (most recent call last):
          File "app.py", line 10, in <module>
            my_func()
          File "app.py", line 7, in my_func
            raise ValueError("An error")
        ValueError: An error
        """
    ).strip()

    details_list = [{"message": "not interested in this field", "rawStack": short_stack}]
    data = {"details": json.dumps(details_list)}

    expected_stack_block = f"```\n{short_stack}\n```"
    expected_result = f"*rawStack:*\n{expected_stack_block}\n"
    result = format_search_results(data)
    assert result == expected_result


def test_format_search_results_details_with_long_raw_stack():
    """details contains a JSON list with a long rawStack."""
    long_stack = textwrap.dedent(
        """
        Traceback (most recent call last):
          File "app.py", line 10, in <module>
            my_func()
          File "app.py", line 7, in my_func
            raise ValueError("An error")
        ValueError: An error
        Traceback (most recent call last):
          File "app.py", line 10, in <module>
            my_func()
          File "app.py", line 7, in my_func
            raise ValueError("An error")
        ValueError: An error
        Traceback (most recent call last):
          File "app.py", line 10, in <module>
            my_func()
          File "app.py", line 7, in my_func
            raise ValueError("An error")
        ValueError: An error
        Traceback (most recent call last):
          File "app.py", line 10, in <module>
            my_func()
          File "app.py", line 7, in my_func
            raise ValueError("An error")
        ValueError: An error
        """
    ).strip()

    details_list = [{"message": "not interested in this field", "rawStack": long_stack}]
    data = {"details": json.dumps(details_list)}

    all_lines = long_stack.splitlines()
    expected_first_10 = "\n".join(all_lines[:10])
    expected_last_10 = "\n".join(all_lines[-10:])

    expected_stack_block = f"```\n{expected_first_10}\n ... \n{expected_last_10}\n```"

    expected_result = f"*rawStack:*\n{expected_stack_block}\n"
    result = format_search_results(data)
    assert result == expected_result


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


@pytest.fixture
def mock_http_request(mocker):
    """Creates a mock azure.functions.HttpRequest."""
    mock = mocker.MagicMock(spec=func.HttpRequest)
    mock.params = {}
    return mock


@pytest.mark.usefixtures("mock_http_response")
def test_alert_to_slack_success(mocker, mock_http_request, sample_alert_data):
    """Test a successful alert_to_slack."""
    mock_url = "http://mock.slack.url"
    mocker.patch("azure_functions.function_app.SLACK_WEBHOOK_URL", mock_url)

    # Mock a valid function key
    mock_http_request.params["code"] = "valid_key"
    mock_validate = mocker.patch("azure_functions.function_app.validate_function_key", return_value=None)

    # Mock JSON success
    mock_http_request.get_json.return_value = {"data": sample_alert_data}

    # Mock a message to Slack
    mock_msg = "Mocked Slack Message"
    mock_build = mocker.patch("azure_functions.function_app.build_slack_message", return_value=mock_msg)

    # Mock response from requests
    mock_post_response = mocker.MagicMock()
    mock_post_response.raise_for_status.return_value = None
    mock_post_response.status_code = 200
    mock_post = mocker.patch("azure_functions.function_app.requests.post", return_value=mock_post_response)

    response = alert_to_slack(mock_http_request)

    mock_validate.assert_called_once_with("valid_key")
    mock_http_request.get_json.assert_called_once()
    mock_build.assert_called_once_with(sample_alert_data)
    mock_post.assert_called_once_with(mock_url, json={"text": mock_msg})
    assert response == ("Alert successfully forwarded to Slack.", 200)


@pytest.mark.usefixtures("mock_http_response")
def test_alert_to_slack_invalid_key(mocker, mock_http_request):
    """Test an invalid key provided to alert_to_slack."""
    auth_fail_response = ("Unauthorized", 401)
    mock_validate = mocker.patch(
        "azure_functions.function_app.validate_function_key",
        return_value=auth_fail_response,
    )
    mock_http_request.params["code"] = "invalid_key"

    response = alert_to_slack(mock_http_request)

    mock_validate.assert_called_once_with("invalid_key")
    assert response == auth_fail_response


@pytest.mark.usefixtures("mock_http_response")
def test_health_check(mocker):
    """
    Test the health_check endpoint.
    """
    mock_req = mocker.MagicMock()

    response = health_check(mock_req)

    assert response == ("Healthy.", 200)
