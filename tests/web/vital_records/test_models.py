from uuid import uuid4
import pytest

from web.vital_records.models import VitalRecordsRequest


def test_get_with_status__matching_request(mocker):
    test_uuid = uuid4()
    mock_request = VitalRecordsRequest(id=test_uuid, status="initialized")
    mock_filter = mocker.patch.object(VitalRecordsRequest.objects, "filter")
    mock_filter.return_value.first.return_value = mock_request

    result = VitalRecordsRequest.get_with_status(test_uuid, "initialized")

    mock_filter.assert_called_once_with(pk=test_uuid)
    assert result == mock_request


def test_get_with_status__no_request(mocker):
    test_uuid = uuid4()
    mock_filter = mocker.patch.object(VitalRecordsRequest.objects, "filter")
    mock_filter.return_value.first.return_value = None

    with pytest.raises(ValueError, match=f"Couldn't find VitalRecordsRequest: {test_uuid}"):
        VitalRecordsRequest.get_with_status(test_uuid, "initialized")


def test_get_with_status__wrong_status(mocker):
    test_uuid = uuid4()
    mock_request = VitalRecordsRequest(id=test_uuid, status="started")
    mock_filter = mocker.patch.object(VitalRecordsRequest.objects, "filter")
    mock_filter.return_value.first.return_value = mock_request

    with pytest.raises(ValueError, match=f"VitalRecordsRequest: {test_uuid} has an invalid status"):
        VitalRecordsRequest.get_with_status(test_uuid, "initialized")


def test_get_finished(db):
    # Create test records with different statuses
    finished_request1 = VitalRecordsRequest.objects.create(status="finished", fire="eaton")
    finished_request2 = VitalRecordsRequest.objects.create(status="finished", fire="hurst")
    VitalRecordsRequest.objects.create(status="submitted", fire="lidia")
    VitalRecordsRequest.objects.create(status="initialized", fire="palisades")

    # Call the method
    finished_requests = VitalRecordsRequest.get_finished()

    # Assert results
    assert len(finished_requests) == 2
    assert set(finished_requests) == {finished_request1, finished_request2}
    for request in finished_requests:
        assert request.status == "finished"
