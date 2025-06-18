import datetime
import os

from django.utils import timezone
import pytest

from web.vital_records import tasks


@pytest.fixture
def mock_PdfReader(mocker):
    return mocker.patch.object(tasks, "PdfReader")


@pytest.fixture
def mock_PdfWriter(mocker):
    return mocker.patch.object(tasks, "PdfWriter")


@pytest.fixture
def mock_VitalRecordsRequest(mocker):
    return mocker.patch.object(tasks, "VitalRecordsRequest")


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
