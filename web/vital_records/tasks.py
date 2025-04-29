import logging
import os
from uuid import UUID, uuid4

from dataclasses import asdict, dataclass
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMessage

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject

from web.core.tasks import Task
from web.vital_records.models import VitalRecordsRequest

logger = logging.getLogger(__name__)

TEMPLATE = os.path.join(settings.BASE_DIR, "web", "vital_records", "templates", "package", "SOE_B.pdf")


@dataclass
class Package:
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

    def make_package(self, request: VitalRecordsRequest):
        package = Package(
            package_id=str(request.pk),
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

        reader = PdfReader(TEMPLATE)
        writer = PdfWriter()
        writer.append(reader)
        writer.update_page_form_field_values(writer.pages[0], package.dict(), auto_regenerate=False)

        written_page = writer.pages[0]

        # get the page's annotations (where form fields are stored)
        for annot in written_page.get("/Annots", []):
            # the annotation might be an indirect reference, so get the object
            annot_object = annot.get_object()
            # check if the annotation is a form field (widget annotation) by looking for '/T' (Field Name)
            if "/T" in annot_object:
                # get the current field flags, default to 0 if not present
                current_flags = annot_object.get("/Ff", 0)

                # Set the read-only flag (the first bit, value 1)
                # Use bitwise OR to add the read-only flag without removing others.
                # The PDF specification defines the first bit (value 1) of the /Ff flag as the ReadOnly flag
                # See Table 8.70 "Field flags common to all field types"
                # https://www.verypdf.com/document/pdf-format-reference/pg_0676.htm
                new_flags = current_flags | 1

                # Update the field flags in the annotation object
                annot_object[NameObject("/Ff")] = NumberObject(new_flags)

        filename = os.path.join(settings.STORAGE_DIR, f"vital-records-{package.package_id}.pdf")
        with open(filename, "wb") as output_stream:
            writer.write(output_stream)

        return filename

    def handler(self, request_id: UUID):
        logger.debug(f"Creating request package for: {request_id}")
        request = get_request_with_status(request_id, "enqueued")

        filename = self.make_package(request)

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
            from_email=settings.VITAL_RECORDS_EMAIL_FROM,
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
