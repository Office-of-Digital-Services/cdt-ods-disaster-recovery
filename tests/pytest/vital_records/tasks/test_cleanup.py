import datetime
import pytest
from web.vital_records.tasks.cleanup import CleanupTask, run_cleanup_task


@pytest.fixture
def mock_Path(mocker):
    return mocker.patch("web.vital_records.tasks.cleanup.Path")


@pytest.fixture
def mock_VitalRecordsRequest(mocker, mock_VitalRecordsRequest):
    mocker.patch("web.vital_records.tasks.cleanup.VitalRecordsRequest", mock_VitalRecordsRequest)
    return mock_VitalRecordsRequest


@pytest.fixture
def mock_VitalRecordsRequestMetadata(mocker):
    return mocker.patch("web.vital_records.tasks.cleanup.VitalRecordsRequestMetadata")


def test_run_cleanup_task(mocker):
    mock_task = mocker.MagicMock()
    mock_CleanupTask = mocker.patch("web.vital_records.tasks.cleanup.CleanupTask", return_value=mock_task)

    result = run_cleanup_task()

    mock_CleanupTask.assert_called_once()
    mock_task.run.assert_called_once()
    assert result == mock_task


class TestCleanupScheduledTask:
    @pytest.fixture
    def task(self) -> CleanupTask:
        return CleanupTask()

    @pytest.fixture
    def mock_clean_file(self, mocker, task):
        return mocker.patch.object(task, "clean_file")

    @pytest.fixture
    def mock_clean_record(self, mocker, task):
        return mocker.patch.object(task, "clean_record")

    @pytest.fixture
    def mock_clean_request(self, mocker, task):
        return mocker.patch.object(task, "clean_request")

    @pytest.fixture
    def mock_create_metadata(self, mocker, task):
        return mocker.patch.object(task, "create_metadata")

    def test_task(self, task):
        assert task.group == "vital-records"
        assert task.name == "cleanup"
        assert task.started is False

    def test_clean_file__file_doesnt_exist(self, mock_VitalRecordsRequest, mock_Path, task: CleanupTask):
        mock_path = mock_Path.return_value
        mock_path.exists.return_value = False
        mock_path.is_file.return_value = False

        result = task.clean_file(mock_VitalRecordsRequest)

        assert result is True

    def test_clean_file__file_not_file(self, mock_VitalRecordsRequest, mock_Path, task: CleanupTask):
        mock_path = mock_Path.return_value
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = False

        result = task.clean_file(mock_VitalRecordsRequest)

        assert result is False

    def test_clean_file(self, mock_VitalRecordsRequest, mock_Path, task: CleanupTask):
        mock_path = mock_Path.return_value
        # the first time the file should exist, and the second time it should not
        mock_path.exists.side_effect = [True, False]
        mock_path.is_file.return_value = True

        result = task.clean_file(mock_VitalRecordsRequest)

        assert result is True
        mock_path.unlink.assert_called_once()

    def test_clean_record__ValueError(self, mock_VitalRecordsRequest, task: CleanupTask):
        mock_VitalRecordsRequest.delete.side_effect = ValueError()
        result = task.clean_record(mock_VitalRecordsRequest)

        mock_VitalRecordsRequest.delete.assert_called_once()
        assert result is False

    def test_clean_record(self, mock_VitalRecordsRequest, task: CleanupTask):
        mock_VitalRecordsRequest.delete.return_value = (1, 1)

        result = task.clean_record(mock_VitalRecordsRequest)

        mock_VitalRecordsRequest.delete.assert_called_once()
        assert result is True

    def test_clean_request__record_fails(
        self, mock_VitalRecordsRequest, mock_clean_record, mock_clean_file, task: CleanupTask
    ):
        mock_clean_record.return_value = False

        result = task.clean_request(mock_VitalRecordsRequest)

        mock_clean_record.assert_called_once()
        mock_clean_file.assert_not_called()
        assert result is False

    def test_clean_request__file_fails(self, mock_VitalRecordsRequest, mock_clean_record, mock_clean_file, task: CleanupTask):
        mock_clean_record.return_value = True
        mock_clean_file.return_value = False

        result = task.clean_request(mock_VitalRecordsRequest)

        mock_clean_record.assert_called_once_with(mock_VitalRecordsRequest)
        mock_clean_file.assert_called_once_with(mock_VitalRecordsRequest)
        assert result is False

    def test_clean_request(self, mock_VitalRecordsRequest, mock_clean_record, mock_clean_file, task: CleanupTask):
        mock_clean_record.return_value = True
        mock_clean_file.return_value = True

        result = task.clean_request(mock_VitalRecordsRequest)

        mock_clean_record.assert_called_once_with(mock_VitalRecordsRequest)
        mock_clean_file.assert_called_once_with(mock_VitalRecordsRequest)
        assert result is True

    def test_create_metadata(self, mocker, mock_VitalRecordsRequest, mock_VitalRecordsRequestMetadata, task: CleanupTask):
        now = datetime.datetime.now()
        mock_timezone = mocker.patch("web.vital_records.tasks.cleanup.timezone")
        mock_timezone.now.return_value = now

        mock_metadata = mock_VitalRecordsRequestMetadata.objects.create.return_value

        task.create_metadata(mock_VitalRecordsRequest)

        mock_VitalRecordsRequestMetadata.objects.create.assert_called_once_with(
            request_id=mock_VitalRecordsRequest.id,
            fire=mock_VitalRecordsRequest.fire,
            number_of_records=mock_VitalRecordsRequest.number_of_records,
            submitted_at=mock_VitalRecordsRequest.submitted_at,
            enqueued_at=mock_VitalRecordsRequest.enqueued_at,
            packaged_at=mock_VitalRecordsRequest.packaged_at,
            sent_at=mock_VitalRecordsRequest.sent_at,
            cleaned_at=now,
        )

        mock_metadata.save.assert_called_once()

    def test_handler__no_batch(
        self,
        mocker,
        mock_VitalRecordsRequest,
        mock_clean_request,
        mock_create_metadata,
        task: CleanupTask,
    ):
        mock_batch = mocker.MagicMock()
        mock_batch.count.return_value = 0
        mock_VitalRecordsRequest.get_finished.return_value = mock_batch

        result = task.handler()

        mock_VitalRecordsRequest.get_finished.assert_called_once()
        mock_clean_request.assert_not_called()
        mock_create_metadata.assert_not_called()
        assert result is True

    def test_handler__batch_fail(
        self,
        mocker,
        mock_VitalRecordsRequest,
        mock_clean_request,
        mock_create_metadata,
        task: CleanupTask,
    ):
        mock_batch = mocker.MagicMock()
        mock_batch.__iter__.return_value = [
            mock_VitalRecordsRequest.return_value,
            mock_VitalRecordsRequest.return_value,
            mock_VitalRecordsRequest.return_value,
        ]
        mock_batch.count.return_value = 3
        mock_VitalRecordsRequest.get_finished.return_value = mock_batch
        # the first and third clean_request succeed, the middle fails
        mock_clean_request.side_effect = [True, False, True]

        result = task.handler()

        mock_VitalRecordsRequest.get_finished.assert_called_once()
        assert mock_create_metadata.call_count == 3
        assert mock_clean_request.call_count == 3
        assert result is False

    def test_handler__batch_success(
        self,
        mocker,
        mock_VitalRecordsRequest,
        mock_clean_request,
        mock_create_metadata,
        task: CleanupTask,
    ):
        mock_batch = mocker.MagicMock()
        mock_batch.__iter__.return_value = [
            mock_VitalRecordsRequest.return_value,
            mock_VitalRecordsRequest.return_value,
            mock_VitalRecordsRequest.return_value,
        ]
        mock_batch.count.return_value = 3
        mock_VitalRecordsRequest.get_finished.return_value = mock_batch

        result = task.handler()

        mock_VitalRecordsRequest.get_finished.assert_called_once()
        assert mock_create_metadata.call_count == 3
        assert mock_clean_request.call_count == 3
        assert result is True
