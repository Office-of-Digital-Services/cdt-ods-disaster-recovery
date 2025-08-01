from uuid import UUID

from web.vital_records.tasks.utils import get_package_filename


def test_get_package_filename(settings):
    """Test get_package_filename returns correct path."""
    test_uuid = UUID("12345678-1234-5678-1234-567812345678")

    result = get_package_filename(test_uuid)
    expected = f"{settings.STORAGE_DIR}/vital-records-12345678-1234-5678-1234-567812345678.pdf"
    assert result == expected


def test_get_package_filename_different_storage(mocker, settings):
    """Test get_package_filename with different storage directory."""
    settings.STORAGE_DIR = "/tmp/storage"
    test_uuid = UUID("12345678-1234-5678-1234-567812345678")

    result = get_package_filename(test_uuid)
    expected = "/tmp/storage/vital-records-12345678-1234-5678-1234-567812345678.pdf"
    assert result == expected
