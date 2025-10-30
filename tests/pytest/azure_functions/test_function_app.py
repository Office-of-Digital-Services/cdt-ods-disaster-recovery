from azure_functions.function_app import select_search_results


def test_select_search_results():
    """Test the selection logic."""
    mock_data = {
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
    result = select_search_results(mock_data)
    expected = {
        "problemId": "pid-123",
        "outerMessage": "Error msg",
        "details": "JSON details",
        "client_City": "TestCity",
        "client_StateOrProvince": "TestState",
        "cloud_RoleInstance": "Instance-1",
    }
    assert result == expected
