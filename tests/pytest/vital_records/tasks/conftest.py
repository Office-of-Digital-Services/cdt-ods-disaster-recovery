import pytest

from web.vital_records.tasks.package import PackageTask


@pytest.fixture
def mock_PackageTask(mocker):
    return mocker.Mock(spec=PackageTask)
