import datetime
import os
import pytest

from django.utils import timezone

from web.vital_records.tasks.package import (
    APPLICATION_TEMPLATE,
    SWORNSTATEMENT_TEMPLATE,
    Application,
    PackageTask,
    SwornStatement,
    submit_request,
)
from web.vital_records.tasks.utils import get_package_filename


@pytest.fixture
def mock_Path(mocker):
    return mocker.patch("web.vital_records.tasks.package.Path")


@pytest.fixture
def mock_PdfReader(mocker):
    return mocker.patch("web.vital_records.tasks.package.PdfReader")


@pytest.fixture
def mock_PdfWriter(mocker):
    return mocker.patch("web.vital_records.tasks.package.PdfWriter")


@pytest.fixture
def mock_Application(mocker):
    return mocker.patch("web.vital_records.tasks.package.Application")


@pytest.fixture
def mock_SwornStatement(mocker):
    return mocker.patch("web.vital_records.tasks.package.SwornStatement")


@pytest.fixture
def mock_EmailTask(mocker):
    return mocker.patch("web.vital_records.tasks.package.EmailTask")


@pytest.fixture
def mock_VitalRecordsRequest(mocker, mock_VitalRecordsRequest):
    mocker.patch("web.vital_records.tasks.package.VitalRecordsRequest", mock_VitalRecordsRequest)
    return mock_VitalRecordsRequest


@pytest.fixture
def mock_PackageTask(mocker, mock_PackageTask):
    return mocker.patch("web.vital_records.tasks.package.PackageTask", return_value=mock_PackageTask)


def test_templates(settings):
    assert str(settings.BASE_DIR) in APPLICATION_TEMPLATE
    assert os.path.join("vital_records", "templates", "package") in APPLICATION_TEMPLATE
    assert SWORNSTATEMENT_TEMPLATE == APPLICATION_TEMPLATE.replace("application", "sworn-statement")


def test_submit_request(mocker, request_id, mock_PackageTask):
    mock_inst = mocker.MagicMock()
    mock_PackageTask.return_value = mock_inst

    result = submit_request(request_id)

    mock_PackageTask.assert_called_once_with(request_id)
    mock_inst.run.assert_called_once()
    assert result == mock_inst


class TestApplication:
    def test_asdict(self):
        app = Application()

        d = app.dict()

        assert d["package_id"] == app.package_id
        assert d["CDPH_VR_FORMTYPE"] == app.CDPH_VR_FORMTYPE
        assert d["CopyType"] == app.CopyType
        assert d["RelationshipToRegistrant"] == app.RelationshipToRegistrant
        assert d["NumberOfCopies"] == app.NumberOfCopies
        assert d["EventType"] == app.EventType


class TestSwornStatement:
    def test_asdict(self):
        ss = SwornStatement(registrantName="name")

        d = ss.dict()

        assert d["registrantName"] == "name"


class TestPackageTask:
    @pytest.fixture
    def task(self, request_id) -> PackageTask:
        return PackageTask(request_id)

    def test_task(self, request_id, task):
        assert task.group == "vital-records"
        assert task.name == "package"
        assert task.kwargs["request_id"] == request_id
        assert task.started is False

    def test_handler(
        self,
        mocker,
        request_id,
        mock_VitalRecordsRequest,
        mock_PdfReader,
        mock_PdfWriter,
        mock_Application,
        mock_SwornStatement,
        task,
    ):
        now = datetime.datetime.now(tz=datetime.UTC)
        expected_start = now.astimezone(timezone.get_default_timezone()).strftime("%Y-%m-%d %H:%M:%S")
        mock_inst = mocker.MagicMock(
            first_name="First", middle_name="M", last_name="Last", address="address", address_2="address_2", started_at=now
        )
        mock_VitalRecordsRequest.get_with_status.return_value = mock_inst

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
            County=mock_inst.county_of_event,
            RegDOE=mock_inst.date_of_event.strftime("%m/%d/%Y"),
            Parent1FirstName=mock_inst.person_1_first_name,
            Parent1LastName=mock_inst.person_1_last_name,
            Parent2FirstName=mock_inst.person_2_first_name,
            Parent2LastName=mock_inst.person_2_last_name,
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

        mock_PdfReader.assert_any_call(APPLICATION_TEMPLATE)
        mock_PdfReader.assert_any_call(SWORNSTATEMENT_TEMPLATE)
        mock_reader = mock_PdfReader.return_value

        mock_PdfWriter.assert_called_once()
        mock_writer = mock_PdfWriter.return_value
        mock_writer.append.assert_any_call(mock_reader)
        mock_writer.update_page_form_field_values.assert_any_call(mock_writer.pages[0], {}, auto_regenerate=False)
        mock_writer.update_page_form_field_values.assert_any_call(mock_writer.pages[1], {}, auto_regenerate=False)
        mock_writer.write.assert_called_once()

        mock_inst.complete_package.assert_called_once()
        mock_inst.save.assert_called_once()

        assert result == get_package_filename(request_id)

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
