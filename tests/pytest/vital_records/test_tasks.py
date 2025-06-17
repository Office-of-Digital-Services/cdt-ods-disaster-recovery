import os

import pytest

from web.vital_records import tasks


@pytest.fixture
def mock_VitalRecordsRequest(mocker):
    return mocker.patch.object(tasks, "VitalRecordsRequest")


@pytest.fixture
def mock_PackageTask(mocker):
    return mocker.patch.object(tasks, "PackageTask")


def test_templates(settings):
    assert str(settings.BASE_DIR) in tasks.APPLICATION_TEMPLATE
    assert os.path.join("vital_records", "templates", "package") in tasks.APPLICATION_TEMPLATE
    assert tasks.SWORNSTATEMENT_TEMPLATE == tasks.APPLICATION_TEMPLATE.replace("application", "sworn-statement")


def test_get_package_filename(settings, request_id):
    filename = tasks.get_package_filename(request_id)

    assert filename.startswith(str(settings.STORAGE_DIR))
    assert filename.endswith(f"vital-records-{request_id}.pdf")


def test_get_request_with_status__not_found(request_id, mock_VitalRecordsRequest):
    mock_VitalRecordsRequest.objects.filter.return_value.first.return_value = None

    with pytest.raises(RuntimeError, match=f"Couldn't find VitalRecordsRequest: {request_id}"):
        tasks.get_request_with_status(request_id, "status")

    mock_VitalRecordsRequest.objects.filter.assert_called_once_with(pk=request_id)


def test_get_request_with_status__wrong_status(mocker, request_id, mock_VitalRecordsRequest):
    expected_status = "expected"
    wrong_status = "wrong"

    mock_inst = mocker.MagicMock()
    mock_inst.status = wrong_status
    mock_VitalRecordsRequest.objects.filter.return_value.first.return_value = mock_inst

    with pytest.raises(
        RuntimeError,
        match=f"VitalRecordsRequest: {request_id} has an invalid status. Expected: {expected_status}, Actual: {wrong_status}",
    ):
        tasks.get_request_with_status(request_id, expected_status)

    mock_VitalRecordsRequest.objects.filter.assert_called_once_with(pk=request_id)


def test_get_request_with_status(mocker, request_id, mock_VitalRecordsRequest):
    mock_inst = mocker.MagicMock()
    mock_inst.status = "status"
    mock_VitalRecordsRequest.objects.filter.return_value.first.return_value = mock_inst

    result = tasks.get_request_with_status(request_id, "status")

    mock_VitalRecordsRequest.objects.filter.assert_called_once_with(pk=request_id)
    assert result == mock_inst


def test_submit_request(mocker, request_id, mock_PackageTask):
    mock_inst = mocker.MagicMock()
    mock_PackageTask.return_value = mock_inst

    result = tasks.submit_request(request_id)

    mock_PackageTask.assert_called_once_with(request_id)
    mock_inst.run.assert_called_once()
    assert result == mock_inst
