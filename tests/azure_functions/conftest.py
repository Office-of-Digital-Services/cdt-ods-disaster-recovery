import pytest


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
