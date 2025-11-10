import pytest


@pytest.fixture
def mock_http_response(mocker):

    def http_response_side_effect(body, status_code):
        return (body, status_code)

    mock_http_response = mocker.patch("azure.functions.HttpResponse", side_effect=http_response_side_effect)
    return mock_http_response
