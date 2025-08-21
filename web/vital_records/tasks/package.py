from dataclasses import asdict, dataclass
import logging
import os
from typing import Optional
from uuid import UUID, uuid4

from django.conf import settings
from django.utils import timezone
from pypdf import PdfReader, PdfWriter

from web.core.tasks import Task
from web.settings import _filter_empty
from web.vital_records.models import VitalRecordsRequest
from web.vital_records.tasks.email import EmailTask
from web.vital_records.tasks.utils import get_package_filename

logger = logging.getLogger(__name__)

APPLICATION_TEMPLATE = os.path.join(settings.BASE_DIR, "web", "vital_records", "templates", "package", "application_birth.pdf")
SWORNSTATEMENT_TEMPLATE = APPLICATION_TEMPLATE.replace("application_birth.pdf", "sworn-statement.pdf")


def submit_request(request_id: UUID):
    """Submit a user request to the task queue for processing."""
    logger.debug(f"Creating package task for: {request_id}")
    # create a new task instance
    task = PackageTask(request_id)
    # calling task.run() submits the task to the queue for processing
    task.run()
    # if callers want to interrogate the status, etc.
    return task


@dataclass
class Application:
    package_id: str = str(uuid4())
    CDPH_VR_FORMTYPE: str = "WILDFIRE_CDPH_VR_B0A6353F1"
    WildfireName: Optional[str] = None
    CopyType: Optional[str] = "/WLDFREAUTH"
    RelationshipToRegistrant: Optional[str] = "/1"
    NumberOfCopies: Optional[int] = 1
    EventType: Optional[str] = "Birth"
    RegFirstName: Optional[str] = None
    RegMiddleName: Optional[str] = None
    RegLastName: Optional[str] = None
    County: Optional[str] = None
    RegDOE: Optional[str] = None
    Parent1FirstName: Optional[str] = None
    Parent2FirstName: Optional[str] = None
    Parent1LastName: Optional[str] = None
    Parent2LastName: Optional[str] = None
    RequestorFirstName: Optional[str] = None
    RequestorLastName: Optional[str] = None
    RequestorMailingAddress: Optional[str] = None
    RequestorCity: Optional[str] = None
    RequestorZipCode: Optional[str] = None
    RequestorCountry: Optional[str] = None
    RequestorTelephone: Optional[str] = None
    RequestorEmail: Optional[str] = None
    RequestorStateProvince: Optional[str] = None
    Comments: Optional[str] = None
    CDPH_VR_APP_ID: str = None

    def dict(self):
        d = asdict(self)
        return {k: v for k, v in d.items() if v}


@dataclass
class SwornStatement:
    registrantNameRow1: Optional[str] = None
    registrantNameRow2: Optional[str] = None
    registrantNameRow3: Optional[str] = None
    applicantRelationToRegistrantRow1: Optional[str] = None
    applicantRelationToRegistrantRow2: Optional[str] = None
    applicantRelationToRegistrantRow3: Optional[str] = None
    day: Optional[str] = None
    month: Optional[str] = None
    year: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    applicantSignature1: Optional[str] = None
    applicantSignature2: Optional[str] = None
    stateOfNotarization: Optional[str] = None
    countyOfNotarization: Optional[str] = None
    dateOfNotarization: Optional[str] = None
    notarySignature: Optional[str] = None
    notaryNameAndTitle: Optional[str] = None
    applicantName: Optional[str] = None
    registrantName: Optional[str] = None

    def dict(self):
        d = asdict(self)
        return {k: v for k, v in d.items() if v}


class PackageTask(Task):
    group = "vital-records"
    name = "package"

    def __init__(self, request_id: UUID):
        super().__init__(request_id=request_id)

    def handler(self, request_id: UUID):
        logger.debug(f"Creating request package for: {request_id}")
        request = VitalRecordsRequest.get_with_status(request_id, "enqueued")

        application = Application(
            package_id=request_id,
            WildfireName=request.fire.capitalize(),
            NumberOfCopies=request.number_of_records,
            RegFirstName=request.first_name,
            RegMiddleName=request.middle_name,
            RegLastName=request.last_name,
            County=request.county_of_event,
            RegDOE=request.date_of_event.strftime("%m/%d/%Y"),
            Parent1FirstName=request.person_1_first_name,
            Parent1LastName=request.person_1_last_name,
            Parent2FirstName=request.person_2_first_name,
            Parent2LastName=request.person_2_last_name,
            RequestorFirstName=request.order_first_name,
            RequestorLastName=request.order_last_name,
            RequestorMailingAddress=" ".join(_filter_empty((request.address, request.address_2))),
            RequestorCity=request.city,
            RequestorStateProvince=request.state,
            RequestorZipCode=request.zip_code,
            RequestorCountry="United States",
            RequestorEmail=request.email_address,
            RequestorTelephone=request.phone_number,
        )

        # use request.started_at, which is the time just after successful auth through the gateway
        # convert to the local timezone and format for display
        auth_time = request.started_at.astimezone(timezone.get_default_timezone()).strftime("%Y-%m-%d %H:%M:%S")
        sworn_statement = SwornStatement(
            registrantNameRow1=" ".join(_filter_empty((request.first_name, request.middle_name, request.last_name))),
            applicantRelationToRegistrantRow1=request.relationship,
            applicantName=request.legal_attestation,
            applicantSignature1=request.legal_attestation,
            applicantSignature2=f"Authorized via California Identity Gateway {auth_time}",
        )

        app_reader = PdfReader(APPLICATION_TEMPLATE)
        writer = PdfWriter()
        writer.append(app_reader)
        writer.update_page_form_field_values(writer.pages[0], application.dict(), auto_regenerate=False)

        ss_reader = PdfReader(SWORNSTATEMENT_TEMPLATE)
        writer.append(ss_reader)
        writer.update_page_form_field_values(writer.pages[1], sworn_statement.dict(), auto_regenerate=False)

        filename = get_package_filename(request_id)
        with open(filename, "wb") as output_stream:
            writer.write(output_stream)

        request.complete_package()
        request.save()

        logger.debug(f"Request package created for: {request_id}")
        return filename

    def post_handler(self, package_task):
        request_id = package_task.kwargs.get("request_id")
        if package_task.success:
            logger.debug(f"Creating email task for: {request_id}")
            email_task = EmailTask(request_id, package_task.result)
            email_task.run()
        else:
            logger.error(f"Package creation failed for: {request_id}")
