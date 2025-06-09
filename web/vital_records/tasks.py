import logging
import os
from dataclasses import asdict, dataclass
from typing import Optional
from uuid import UUID, uuid4

from django.conf import settings
from django.core.mail import EmailMessage
from pypdf import PdfReader, PdfWriter

from web.core.tasks import Task
from web.vital_records.models import VitalRecordsRequest

logger = logging.getLogger(__name__)

APPLICATION_TEMPLATE = os.path.join(settings.BASE_DIR, "web", "vital_records", "templates", "package", "application.pdf")
SWORNSTATEMENT_TEMPLATE = APPLICATION_TEMPLATE.replace("application.pdf", "sworn-statement.pdf")


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


def get_request_with_status(request_id: UUID, required_status: str):
    request = VitalRecordsRequest.objects.filter(pk=request_id).first()

    if request is None:
        raise RuntimeError(f"Couldn't find VitalRecordsRequest: {request_id}")
    if request.status != required_status:
        raise RuntimeError(
            f"VitalRecordsRequest: {request_id} has an invalid status. Expected: {required_status}, Actual: {request.status}"
        )

    return request


class PackageTask(Task):
    group = "vital-records"
    name = "package"

    def __init__(self, request_id: UUID):
        super().__init__(request_id=request_id)

    def handler(self, request_id: UUID):
        logger.debug(f"Creating request package for: {request_id}")
        request = get_request_with_status(request_id, "enqueued")

        application = Application(
            package_id=request_id,
            WildfireName=request.fire.capitalize(),
            NumberOfCopies=request.number_of_records,
            RegFirstName=request.first_name,
            RegMiddleName=request.middle_name,
            RegLastName=request.last_name,
            County=request.county_of_birth,
            RegDOE=request.date_of_birth.strftime("%m/%d/%Y"),
            Parent1FirstName=request.parent_1_first_name,
            Parent1LastName=request.parent_1_last_name,
            Parent2FirstName=request.parent_2_first_name,
            Parent2LastName=request.parent_2_last_name,
            RequestorFirstName=request.order_first_name,
            RequestorLastName=request.order_last_name,
            RequestorMailingAddress=request.address,
            RequestorCity=request.city,
            RequestorStateProvince=request.state,
            RequestorZipCode=request.zip_code,
            RequestorCountry="United States",
            RequestorEmail=request.email_address,
            RequestorTelephone=request.phone_number,
        )

        app_reader = PdfReader(APPLICATION_TEMPLATE)
        writer = PdfWriter()
        writer.append(app_reader)
        writer.update_page_form_field_values(writer.pages[0], application.dict(), auto_regenerate=False)

        filename = os.path.join(settings.STORAGE_DIR, f"vital-records-{package.package_id}.pdf")
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


class EmailTask(Task):
    group = "vital-records"
    name = "email"

    def __init__(self, request_id: UUID, package: str):
        super().__init__(request_id=request_id, package=package)

    def handler(self, request_id: UUID, package: str):
        logger.debug(f"Sending request package for: {request_id}")
        request = get_request_with_status(request_id, "packaged")

        email = EmailMessage(
            subject="Vital records request",
            body="A new request is attached.",
            to=[settings.VITAL_RECORDS_EMAIL_TO],
            cc=[request.email_address],
        )
        email.attach_file(package, "application/pdf")
        result = email.send()

        request.complete_send()
        request.finish()
        request.save()

        logger.debug(f"Request package sent for: {request_id} with response {result}")

        return result


def submit_request(request_id: UUID):
    """Submit a user request to the task queue for processing."""
    logger.debug(f"Creating package task for: {request_id}")
    # create a new task instance
    task = PackageTask(request_id)
    # calling task.run() submits the task to the queue for processing
    task.run()
    # if callers want to interrogate the status, etc.
    return task
