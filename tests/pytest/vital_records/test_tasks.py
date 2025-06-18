import datetime
import os

import pytest

from web.vital_records import tasks


@pytest.fixture
def mock_EmailMessage(mocker):
    return mocker.patch.object(tasks, "EmailMessage")


@pytest.fixture
def mock_Path(mocker):
    return mocker.patch.object(tasks, "Path")


@pytest.fixture
def mock_PdfReader(mocker):
    return mocker.patch.object(tasks, "PdfReader")


@pytest.fixture
def mock_PdfWriter(mocker):
    return mocker.patch.object(tasks, "PdfWriter")


@pytest.fixture
def mock_VitalRecordsRequest(mocker, request_id):
    req = mocker.patch.object(tasks, "VitalRecordsRequest")
    req.id = request_id
    return req


@pytest.fixture
def mock_VitalRecordsRequestMetadata(mocker):
    return mocker.patch.object(tasks, "VitalRecordsRequestMetadata")


@pytest.fixture
def mock_get_request_with_status(mocker):
    return mocker.patch.object(tasks, "get_request_with_status")


@pytest.fixture
def mock_Package(mocker):
    return mocker.patch.object(tasks, "Package")


@pytest.fixture
def mock_PackageTask(mocker):
    return mocker.patch.object(tasks, "PackageTask")


@pytest.fixture
def mock_EmailTask(mocker):
    return mocker.patch.object(tasks, "EmailTask")


def test_template(settings):
    assert str(settings.BASE_DIR) in tasks.TEMPLATE
    assert os.path.join("vital_records", "templates", "package") in tasks.TEMPLATE


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


class TestPackageTask:
    @pytest.fixture
    def task(self, request_id) -> tasks.PackageTask:
        return tasks.PackageTask(request_id)

    def test_task(self, request_id, task):
        assert task.group == "vital-records"
        assert task.name == "package"
        assert task.kwargs["request_id"] == request_id
        assert task.started is False

    def test_handler(
        self, mocker, request_id, mock_PdfReader, mock_PdfWriter, mock_get_request_with_status, mock_Package, task
    ):
        mock_inst = mocker.MagicMock()
        mock_get_request_with_status.return_value = mock_inst

        mock_pkg = mock_Package.return_value
        mock_pkg.dict.return_value = {}

        result = task.handler(request_id)

        mock_Package.assert_called_once_with(
            package_id=request_id,
            WildfireName=mock_inst.fire.capitalize(),
            NumberOfCopies=mock_inst.number_of_records,
            RegFirstName=mock_inst.first_name,
            RegMiddleName=mock_inst.middle_name,
            RegLastName=mock_inst.last_name,
            County=mock_inst.county_of_birth,
            RegDOE=mock_inst.date_of_birth.strftime("%m/%d/%Y"),
            Parent1FirstName=mock_inst.parent_1_first_name,
            Parent1LastName=mock_inst.parent_1_last_name,
            Parent2FirstName=mock_inst.parent_2_first_name,
            Parent2LastName=mock_inst.parent_2_last_name,
            RequestorFirstName=mock_inst.order_first_name,
            RequestorLastName=mock_inst.order_last_name,
            RequestorMailingAddress=mock_inst.address,
            RequestorCity=mock_inst.city,
            RequestorStateProvince=mock_inst.state,
            RequestorZipCode=mock_inst.zip_code,
            RequestorCountry="United States",
            RequestorEmail=mock_inst.email_address,
            RequestorTelephone=mock_inst.phone_number,
        )

        mock_PdfReader.assert_called_once_with(tasks.TEMPLATE)
        mock_reader = mock_PdfReader.return_value

        mock_PdfWriter.assert_called_once()
        mock_writer = mock_PdfWriter.return_value
        mock_writer.append.assert_called_once_with(mock_reader)
        mock_writer.update_page_form_field_values.assert_called_once_with(mock_writer.pages[0], {}, auto_regenerate=False)
        mock_writer.write.assert_called_once()

        mock_inst.complete_package.assert_called_once()
        mock_inst.save.assert_called_once()

        assert result == tasks.get_package_filename(request_id)

    def test_post_handler__not_success(self, mocker, mock_EmailTask, task):
        patched_task = mocker.MagicMock(wraps=task, success=False)

        task.post_handler(patched_task)

        mock_EmailTask.assert_not_called()

    def test_post_handler__success(self, mocker, request_id, mock_EmailTask, task):
        patched_task = mocker.MagicMock(wraps=task, success=True, result="result")

        task.post_handler(patched_task)

        mock_EmailTask.assert_called_once_with(request_id, patched_task.result)
        mock_email = mock_EmailTask.return_value
        mock_email.run.assert_called_once()


class TestEmailTask:
    @pytest.fixture
    def task(self, request_id, mock_PackageTask) -> tasks.EmailTask:
        mock_package_task = mock_PackageTask.return_value
        mock_package_task.kwargs["request_id"] = request_id
        return tasks.EmailTask(request_id, "package")

    def test_task(self, request_id, task):
        assert task.group == "vital-records"
        assert task.name == "email"
        assert task.kwargs["request_id"] == request_id
        assert task.kwargs["package"] == "package"
        assert task.started is False

    def test_handler(self, settings, mocker, request_id, mock_EmailMessage, mock_get_request_with_status, task):
        mock_email = mock_EmailMessage.return_value
        mock_email.send.return_value = 0

        mock_inst = mocker.MagicMock(email_address="email@example.com")
        mock_get_request_with_status.return_value = mock_inst

        result = task.handler(request_id, "package")

        mock_EmailMessage.assert_called_once_with(
            subject="Vital records request",
            body="A new request is attached.",
            to=[settings.VITAL_RECORDS_EMAIL_TO],
            cc=["email@example.com"],
        )

        mock_email.attach_file.assert_called_once_with("package", "application/pdf")
        mock_email.send.assert_called_once()

        mock_inst.complete_send.assert_called_once()
        mock_inst.finish.assert_called_once()
        mock_inst.save.assert_called_once()

        assert result == 0


class TestCleanupScheduledTask:
    @pytest.fixture
    def task(self) -> type[tasks.CleanupScheduledTask]:
        """Returns the class directly, since we use its @classmethods."""
        return tasks.CleanupScheduledTask

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

    def test_clean_file__file_doesnt_exist(self, request_id, mock_Path, task: type[tasks.CleanupScheduledTask]):
        mock_path = mock_Path.return_value
        mock_path.exists.return_value = False
        mock_path.is_file.return_value = False

        result = task.clean_file(request_id)

        assert result is True

    def test_clean_file__file_not_file(self, request_id, mock_Path, task: type[tasks.CleanupScheduledTask]):
        mock_path = mock_Path.return_value
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = False

        result = task.clean_file(request_id)

        assert result is False

    def test_clean_file(self, request_id, mock_Path, task: type[tasks.CleanupScheduledTask]):
        mock_path = mock_Path.return_value
        # the first time the file should exist, and the second time it should not
        mock_path.exists.side_effect = [True, False]
        mock_path.is_file.return_value = True

        result = task.clean_file(request_id)

        assert result is True
        mock_path.unlink.assert_called_once()

    def test_clean_record__ValueError(self, request_id, mock_VitalRecordsRequest, task: type[tasks.CleanupScheduledTask]):
        result = task.clean_record(mock_VitalRecordsRequest)

        mock_VitalRecordsRequest.delete.assert_called_once()
        assert result is False

    def test_clean_record(self, request_id, mock_VitalRecordsRequest, task: type[tasks.CleanupScheduledTask]):
        mock_VitalRecordsRequest.delete.return_value = (1, 1)

        result = task.clean_record(mock_VitalRecordsRequest)

        mock_VitalRecordsRequest.delete.assert_called_once()
        assert result is True

    def test_clean_request__record_fails(
        self, mock_VitalRecordsRequest, mock_clean_record, mock_clean_file, task: type[tasks.CleanupScheduledTask]
    ):
        mock_clean_record.return_value = False

        result = task.clean_request(mock_VitalRecordsRequest)

        mock_clean_record.assert_called_once()
        mock_clean_file.assert_not_called()
        assert result is False

    def test_clean_request__file_fails(
        self, request_id, mock_VitalRecordsRequest, mock_clean_record, mock_clean_file, task: type[tasks.CleanupScheduledTask]
    ):
        mock_clean_record.return_value = True
        mock_clean_file.return_value = False

        result = task.clean_request(mock_VitalRecordsRequest)

        mock_clean_record.assert_called_once_with(mock_VitalRecordsRequest)
        mock_clean_file.assert_called_once_with(request_id)
        assert result is False

    def test_clean_request(
        self, request_id, mock_VitalRecordsRequest, mock_clean_record, mock_clean_file, task: type[tasks.CleanupScheduledTask]
    ):
        mock_clean_record.return_value = True
        mock_clean_file.return_value = True

        result = task.clean_request(mock_VitalRecordsRequest)

        mock_clean_record.assert_called_once_with(mock_VitalRecordsRequest)
        mock_clean_file.assert_called_once_with(request_id)
        assert result is True

    def test_create_metadata(
        self, mocker, mock_VitalRecordsRequest, mock_VitalRecordsRequestMetadata, task: type[tasks.CleanupScheduledTask]
    ):
        now = datetime.datetime.now()
        mock_timezone = mocker.patch.object(tasks, "timezone")
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
        task: type[tasks.CleanupScheduledTask],
    ):
        mock_batch = mocker.MagicMock()
        mock_batch.count.return_value = 0
        mock_VitalRecordsRequest.objects.filter.return_value = mock_batch

        result = task.handler()

        mock_VitalRecordsRequest.objects.filter.assert_called_once_with(status="finished")
        mock_clean_request.assert_not_called()
        mock_create_metadata.assert_not_called()
        assert result is True

    def test_handler__batch_fail(
        self,
        mocker,
        mock_VitalRecordsRequest,
        mock_clean_request,
        mock_create_metadata,
        task: type[tasks.CleanupScheduledTask],
    ):
        mock_batch = mocker.MagicMock()
        mock_batch.__iter__.return_value = [
            mock_VitalRecordsRequest.return_value,
            mock_VitalRecordsRequest.return_value,
            mock_VitalRecordsRequest.return_value,
        ]
        mock_batch.count.return_value = 3
        mock_VitalRecordsRequest.objects.filter.return_value = mock_batch
        # the first and third clean_request succeed, the middle fails
        mock_clean_request.side_effect = [True, False, True]

        result = task.handler()

        mock_VitalRecordsRequest.objects.filter.assert_called_once_with(status="finished")
        assert mock_create_metadata.call_count == 3
        assert mock_clean_request.call_count == 3
        assert result is False

    def test_handler__batch_success(
        self,
        mocker,
        mock_VitalRecordsRequest,
        mock_clean_request,
        mock_create_metadata,
        task: type[tasks.CleanupScheduledTask],
    ):
        mock_batch = mocker.MagicMock()
        mock_batch.__iter__.return_value = [
            mock_VitalRecordsRequest.return_value,
            mock_VitalRecordsRequest.return_value,
            mock_VitalRecordsRequest.return_value,
        ]
        mock_batch.count.return_value = 3
        mock_VitalRecordsRequest.objects.filter.return_value = mock_batch

        result = task.handler()

        mock_VitalRecordsRequest.objects.filter.assert_called_once_with(status="finished")
        assert mock_create_metadata.call_count == 3
        assert mock_clean_request.call_count == 3
        assert result is True
