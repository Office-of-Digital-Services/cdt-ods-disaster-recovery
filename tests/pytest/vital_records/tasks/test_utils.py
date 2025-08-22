import pytest
from datetime import datetime, timezone
from uuid import UUID

from web.vital_records.models import VitalRecordsRequest
from web.vital_records.tasks.utils import get_package_filename


@pytest.fixture
def mock_VitalRecordsRequest(mocker):
    mock_instance = mocker.MagicMock(spec=VitalRecordsRequest)
    mock_instance.id = UUID("12345678-1234-5678-1234-567812345678")
    mock_instance.type = "birth"
    mock_instance.submitted_at = datetime(2025, 8, 21, 19, 17, 58, tzinfo=timezone.utc)

    return mock_instance


def test_get_package_filename(settings, mock_VitalRecordsRequest):
    """Test get_package_filename returns correct path."""

    result = get_package_filename(mock_VitalRecordsRequest)
    expected = f"{settings.STORAGE_DIR}/vital-records-2025-08-21-birth-12345678-1234-5678-1234-567812345678.pdf"
    assert result == expected


def test_get_package_filename_different_storage(settings, mock_VitalRecordsRequest):
    """Test get_package_filename with different storage directory."""
    settings.STORAGE_DIR = "/tmp/storage"

    result = get_package_filename(mock_VitalRecordsRequest)
    expected = "/tmp/storage/vital-records-2025-08-21-birth-12345678-1234-5678-1234-567812345678.pdf"
    assert result == expected
