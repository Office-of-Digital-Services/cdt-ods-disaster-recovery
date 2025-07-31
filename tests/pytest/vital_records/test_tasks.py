import datetime
import os

from django.utils import timezone
import pytest

from web.vital_records import tasks


@pytest.fixture
def mock_EmailMessage(mocker):
    return mocker.patch.object(tasks, "EmailMultiAlternatives")


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
def mock_Application(mocker):
    return mocker.patch.object(tasks, "Application")


@pytest.fixture
def mock_SwornStatement(mocker):
    return mocker.patch.object(tasks, "SwornStatement")


@pytest.fixture
def mock_PackageTask(mocker):
    return mocker.patch.object(tasks, "PackageTask")


@pytest.fixture
def mock_EmailTask(mocker):
    return mocker.patch.object(tasks, "EmailTask")


def test_templates(settings):
    assert str(settings.BASE_DIR) in tasks.APPLICATION_TEMPLATE
    assert os.path.join("vital_records", "templates", "package") in tasks.APPLICATION_TEMPLATE
    assert tasks.SWORNSTATEMENT_TEMPLATE == tasks.APPLICATION_TEMPLATE.replace("application", "sworn-statement")


def test_get_package_filename(settings, request_id):
    filename = tasks.get_package_filename(request_id)

    assert filename.startswith(str(settings.STORAGE_DIR))
    assert filename.endswith(f"vital-records-{request_id}.pdf")


def test_submit_request(mocker, request_id, mock_PackageTask):
    mock_inst = mocker.MagicMock()
    mock_PackageTask.return_value = mock_inst

    result = tasks.submit_request(request_id)

    mock_PackageTask.assert_called_once_with(request_id)
    mock_inst.run.assert_called_once()
    assert result == mock_inst


class TestApplication:
    def test_asdict(self):
        app = tasks.Application()

        d = app.dict()

        assert d["package_id"] == app.package_id
        assert d["CDPH_VR_FORMTYPE"] == app.CDPH_VR_FORMTYPE
        assert d["CopyType"] == app.CopyType
        assert d["RelationshipToRegistrant"] == app.RelationshipToRegistrant
        assert d["NumberOfCopies"] == app.NumberOfCopies
        assert d["EventType"] == app.EventType


class TestSwornStatement:
    def test_asdict(self):
        ss = tasks.SwornStatement(registrantName="name")

        d = ss.dict()

        assert d["registrantName"] == "name"


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
        self,
        mocker,
        request_id,
        mock_PdfReader,
        mock_PdfWriter,
        mock_get_request_with_status,
        mock_Application,
        mock_SwornStatement,
        task,
    ):
        now = datetime.datetime.now(tz=datetime.UTC)
        expected_start = now.astimezone(timezone.get_default_timezone()).strftime("%Y-%m-%d %H:%M:%S")
        mock_inst = mocker.MagicMock(
            first_name="First", middle_name="M", last_name="Last", address="address", address_2="address_2", started_at=now
        )
        mock_get_request_with_status.return_value = mock_inst

        mock_app = mock_Application.return_value
        mock_app.dict.return_value = {}
        mock_ss = mock_SwornStatement.return_value
        mock_ss.dict.return_value = {}

        result = task.handler(request_id)

        mock_Application.assert_called_once_with(
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
            RequestorMailingAddress=mock_inst.address + " " + mock_inst.address_2,
            RequestorCity=mock_inst.city,
            RequestorStateProvince=mock_inst.state,
            RequestorZipCode=mock_inst.zip_code,
            RequestorCountry="United States",
            RequestorEmail=mock_inst.email_address,
            RequestorTelephone=mock_inst.phone_number,
        )

        mock_SwornStatement.assert_called_once_with(
            registrantNameRow1="First M Last",
            applicantRelationToRegistrantRow1=mock_inst.relationship,
            applicantName=mock_inst.legal_attestation,
            applicantSignature1=mock_inst.legal_attestation,
            applicantSignature2=f"Authorized via California Identity Gateway {expected_start}",
        )

        mock_PdfReader.assert_any_call(tasks.APPLICATION_TEMPLATE)
        mock_PdfReader.assert_any_call(tasks.SWORNSTATEMENT_TEMPLATE)
        mock_reader = mock_PdfReader.return_value

        mock_PdfWriter.assert_called_once()
        mock_writer = mock_PdfWriter.return_value
        mock_writer.append.assert_any_call(mock_reader)
        mock_writer.update_page_form_field_values.assert_any_call(mock_writer.pages[0], {}, auto_regenerate=False)
        mock_writer.update_page_form_field_values.assert_any_call(mock_writer.pages[1], {}, auto_regenerate=False)
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
        mock_render = mocker.patch.object(tasks, "render_to_string", return_value="email body")

        mock_email = mock_EmailMessage.return_value
        mock_email.send.return_value = 0

        mock_inst = mocker.MagicMock(email_address="email@example.com", number_of_records=3)
        mock_get_request_with_status.return_value = mock_inst

        result = task.handler(request_id, "package")

        expected_ctx = {
            "number_of_copies": mock_inst.number_of_records,
            "email_address": mock_inst.email_address,
            "logo_url": "https://webstandards.ca.gov/wp-content/uploads/sites/8/2024/10/cagov-logo-coastal-flat.png",
        }
        mock_render.assert_any_call(tasks.EMAIL_TXT_TEMPLATE, expected_ctx)
        mock_render.assert_any_call(tasks.EMAIL_HTML_TEMPLATE, expected_ctx)

        mock_EmailMessage.assert_called_once_with(
            subject="Completed: Birth Record Request",
            body=mock_render.return_value,
            to=[settings.VITAL_RECORDS_EMAIL_TO],
        )

        mock_email.attach_alternative.assert_called_once_with(mock_render.return_value, "text/html")
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
