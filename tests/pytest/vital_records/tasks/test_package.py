import datetime
import os
import pytest

from django.utils import timezone

from web.settings import _filter_empty
from web.vital_records.models import VitalRecordsRequest
from web.vital_records.tasks.package import (
    APPLICATION_FOLDER,
    SWORNSTATEMENT_TEMPLATE,
    BirthApplication,
    MarriageApplication,
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
def mock_BirthApplication(mocker):
    return mocker.patch("web.vital_records.tasks.package.BirthApplication")


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


@pytest.fixture
def mock_vital_records_request(mocker):
    mock_request = mocker.MagicMock(spec=VitalRecordsRequest)
    mock_request.fire = "palisades"
    mock_request.number_of_records = 2
    mock_request.relationship = "Relationship"
    mock_request.legal_attestation = "Legal Attestation"
    mock_request.first_name = "Jane"
    mock_request.middle_name = "Anne"
    mock_request.last_name = "Doe"
    mock_request.county_of_event = "Los Angeles"
    mock_request.date_of_event = datetime.datetime(2025, 8, 21, 19, 17, 58, tzinfo=datetime.UTC)
    mock_request.person_1_first_name = "First1"
    mock_request.person_1_middle_name = "Middle1"
    mock_request.person_1_last_name = "Last1"
    mock_request.person_2_first_name = "First2"
    mock_request.person_2_middle_name = "Middle2"
    mock_request.person_2_last_name = "Last2"
    mock_request.order_first_name = "Requester"
    mock_request.order_last_name = "Person"
    mock_request.address = "123 Main St"
    mock_request.address_2 = "Apt 4A"
    mock_request.city = "Los Angeles"
    mock_request.state = "CA"
    mock_request.zip_code = "90012"
    mock_request.email_address = "test@example.com"
    mock_request.phone_number = "3231234567"

    return mock_request


def test_templates(settings):
    assert str(settings.BASE_DIR) in APPLICATION_FOLDER
    assert os.path.join("vital_records", "templates", "package") in APPLICATION_FOLDER
    assert SWORNSTATEMENT_TEMPLATE == os.path.join(APPLICATION_FOLDER, "sworn-statement.pdf")


def test_submit_request(mocker, request_id, mock_PackageTask):
    mock_inst = mocker.MagicMock()
    mock_PackageTask.return_value = mock_inst

    result = submit_request(request_id)

    mock_PackageTask.assert_called_once_with(request_id)
    mock_inst.run.assert_called_once()
    assert result == mock_inst


class TestBirthApplication:
    def test_asdict(self):
        app = BirthApplication()

        d = app.dict()

        assert d["package_id"] == app.package_id
        assert d["CDPH_VR_FORMTYPE"] == app.CDPH_VR_FORMTYPE
        assert d["CopyType"] == app.CopyType
        assert d["RelationshipToRegistrant"] == app.RelationshipToRegistrant
        assert d["NumberOfCopies"] == app.NumberOfCopies
        assert d["EventType"] == app.EventType

    def test_create(self, mock_vital_records_request, request_id):
        mock_vital_records_request.id = request_id

        application = BirthApplication.create(mock_vital_records_request)

        assert isinstance(application, BirthApplication)
        assert application.package_id == mock_vital_records_request.id
        assert application.WildfireName == mock_vital_records_request.fire.capitalize()
        assert application.NumberOfCopies == mock_vital_records_request.number_of_records
        assert application.RegFirstName == mock_vital_records_request.first_name
        assert application.RegMiddleName == mock_vital_records_request.middle_name
        assert application.RegLastName == mock_vital_records_request.last_name
        assert application.County == mock_vital_records_request.county_of_event
        assert application.RegDOE == mock_vital_records_request.date_of_event.strftime("%m/%d/%Y")
        assert application.Parent1FirstName == mock_vital_records_request.person_1_first_name
        assert application.Parent1LastName == mock_vital_records_request.person_1_last_name
        assert application.Parent2FirstName == mock_vital_records_request.person_2_first_name
        assert application.Parent2LastName == mock_vital_records_request.person_2_last_name
        assert application.RequestorFirstName == mock_vital_records_request.order_first_name
        assert application.RequestorLastName == mock_vital_records_request.order_last_name
        assert application.RequestorMailingAddress == " ".join(
            _filter_empty((mock_vital_records_request.address, mock_vital_records_request.address_2))
        )
        assert application.RequestorCity == mock_vital_records_request.city
        assert application.RequestorStateProvince == mock_vital_records_request.state
        assert application.RequestorZipCode == mock_vital_records_request.zip_code
        assert application.RequestorCountry == "United States"
        assert application.RequestorEmail == mock_vital_records_request.email_address
        assert application.RequestorTelephone == mock_vital_records_request.phone_number


class TestMarriageApplication:
    def test_asdict(self):
        app = MarriageApplication()

        d = app.dict()

        assert d["package_id"] == app.package_id
        assert d["CDPH_VR_FORMTYPE"] == app.CDPH_VR_FORMTYPE
        assert d["CopyType"] == app.CopyType
        assert d["RelationshipToRegistrant"] == app.RelationshipToRegistrant
        assert d["NumberOfCopies"] == app.NumberOfCopies
        assert d["EventType"] == app.EventType

    def test_create(self, mock_vital_records_request, request_id):
        mock_vital_records_request.id = request_id

        application = MarriageApplication.create(mock_vital_records_request)

        assert isinstance(application, MarriageApplication)
        assert application.package_id == mock_vital_records_request.id
        assert application.WildfireName == mock_vital_records_request.fire.capitalize()
        assert application.NumberOfCopies == mock_vital_records_request.number_of_records
        assert application.Spouse1FirstName == mock_vital_records_request.person_1_first_name
        assert application.Spouse1MiddleName == mock_vital_records_request.person_1_middle_name
        assert application.Spouse1LastName == mock_vital_records_request.person_1_last_name
        assert application.Spouse1BirthLastName == mock_vital_records_request.person_1_birth_last_name
        assert application.Spouse2FirstName == mock_vital_records_request.person_2_first_name
        assert application.Spouse2MiddleName == mock_vital_records_request.person_2_middle_name
        assert application.Spouse2LastName == mock_vital_records_request.person_2_last_name
        assert application.Spouse2BirthLastName == mock_vital_records_request.person_2_birth_last_name
        assert application.County == mock_vital_records_request.county_of_event
        assert application.RegDOE == mock_vital_records_request.date_of_event.strftime("%m/%d/%Y")
        assert application.RequestorFirstName == mock_vital_records_request.order_first_name
        assert application.RequestorLastName == mock_vital_records_request.order_last_name
        assert application.RequestorMailingAddress == " ".join(
            _filter_empty((mock_vital_records_request.address, mock_vital_records_request.address_2))
        )
        assert application.RequestorCity == mock_vital_records_request.city
        assert application.RequestorStateProvince == mock_vital_records_request.state
        assert application.RequestorZipCode == mock_vital_records_request.zip_code
        assert application.RequestorCountry == "United States"
        assert application.RequestorEmail == mock_vital_records_request.email_address
        assert application.RequestorTelephone == mock_vital_records_request.phone_number


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

    def test__get_birth_sworn_statement(self, mock_vital_records_request, task):
        now = datetime.datetime.now(tz=datetime.UTC)
        mock_vital_records_request.started_at = now

        sworn_statement = task._get_birth_sworn_statement(mock_vital_records_request)

        assert isinstance(sworn_statement, SwornStatement)
        assert sworn_statement.applicantName == "Legal Attestation"
        assert sworn_statement.applicantSignature1 == "Legal Attestation"
        assert sworn_statement.applicantSignature2 == (
            f"Authorized via California Identity Gateway "
            f"{now.astimezone(timezone.get_default_timezone()).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        assert sworn_statement.registrantNameRow1 == "Jane Anne Doe"
        assert sworn_statement.applicantRelationToRegistrantRow1 == "Relationship"

    def test__get_marriage_sworn_statement(self, mock_vital_records_request, task):
        now = datetime.datetime.now(tz=datetime.UTC)
        mock_vital_records_request.started_at = now

        sworn_statement = task._get_marriage_sworn_statement(mock_vital_records_request)

        assert isinstance(sworn_statement, SwornStatement)
        assert sworn_statement.applicantName == "Legal Attestation"
        assert sworn_statement.applicantSignature1 == "Legal Attestation"
        assert sworn_statement.applicantSignature2 == (
            f"Authorized via California Identity Gateway "
            f"{now.astimezone(timezone.get_default_timezone()).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        assert sworn_statement.registrantNameRow1 == "F. Last1 / F. Last2"
        assert sworn_statement.applicantRelationToRegistrantRow1 == "Relationship"

    @pytest.mark.parametrize(
        "request_type, mock_app_class, mock_ss_helper_method_name",
        [
            ("birth", BirthApplication, "_get_birth_sworn_statement"),
            ("marriage", MarriageApplication, "_get_marriage_sworn_statement"),
        ],
    )
    def test_handler(
        self,
        mocker,
        request_id,
        mock_VitalRecordsRequest,
        mock_PdfReader,
        mock_PdfWriter,
        task,
        request_type,
        mock_app_class,
        mock_ss_helper_method_name,
    ):
        now = datetime.datetime.now(tz=datetime.UTC)
        mock_inst = mocker.MagicMock(
            first_name="First",
            middle_name="M",
            last_name="Last",
            address="address",
            address_2="address_2",
            started_at=now,
            type=request_type,
        )
        mock_VitalRecordsRequest.get_with_status.return_value = mock_inst

        mock_application_obj = mocker.MagicMock()
        mock_application_obj.dict.return_value = {"app_key": "app_value"}
        mocker.patch.object(mock_app_class, "create", return_value=mock_application_obj)

        mock_sworn_statement_obj = mocker.MagicMock()
        mock_sworn_statement_obj.dict.return_value = {}
        mocker.patch.object(task, mock_ss_helper_method_name, return_value=mock_sworn_statement_obj)

        result = task.handler(request_id)

        mock_VitalRecordsRequest.get_with_status.assert_called_once_with(request_id, "enqueued")

        getattr(mock_app_class, "create").assert_called_once_with(mock_inst)
        getattr(task, mock_ss_helper_method_name).assert_called_once_with(mock_inst)

        mock_PdfReader.assert_any_call(os.path.join(APPLICATION_FOLDER, f"application_{request_type}.pdf"))
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

        assert result == get_package_filename(mock_inst)

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
