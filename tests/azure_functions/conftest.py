import pytest


@pytest.fixture
def mock_http_response(mocker):

    def http_response_side_effect(body, status_code):
        return (body, status_code)

    mock_http_response = mocker.patch("azure.functions.HttpResponse", side_effect=http_response_side_effect)
    return mock_http_response


@pytest.fixture
def log_search_result():
    return {
        "columns": [
            {"name": "problemId"},
            {"name": "otherCol"},
            {"name": "outerMessage"},
            {"name": "details"},
            {"name": "client_City"},
            {"name": "client_StateOrProvince"},
            {"name": "cloud_RoleInstance"},
        ],
        "rows": [["pid-123", "ignore", "Error msg", "JSON details", "TestCity", "TestState", "Instance-1"]],
    }
