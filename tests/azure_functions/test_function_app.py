import pytest

from azure_functions.function_app import build_slack_message, format_alert_date, select_search_results, validate_function_key


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
