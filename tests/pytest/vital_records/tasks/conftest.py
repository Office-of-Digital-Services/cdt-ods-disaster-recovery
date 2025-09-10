import pytest

from web.vital_records.models import VitalRecordsRequest
from web.vital_records.tasks.package import PackageTask


@pytest.fixture
def mock_PackageTask(mocker):
    return mocker.Mock(spec=PackageTask)


@pytest.fixture
def mock_VitalRecordsRequest(mocker, request_id):
    mock = mocker.Mock(spec=VitalRecordsRequest, id=request_id)
    mock_inst = mocker.MagicMock(email_address="email@example.com", number_of_records=1)
    mock.get_with_status.return_value = mock_inst
    return mock
