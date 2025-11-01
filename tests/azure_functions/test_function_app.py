from azure_functions.function_app import select_search_results


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
