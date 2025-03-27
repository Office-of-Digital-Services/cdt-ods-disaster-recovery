import logging
import os
import random
from uuid import uuid4

from dataclasses import asdict, dataclass
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMessage

from pypdf import PdfReader, PdfWriter

from web.core.tasks import Task

logger = logging.getLogger(__name__)

TEMPLATE = os.path.join(settings.BASE_DIR, "web", "vital_records", "templates", "package", "SOE_B.pdf")


@dataclass
class Package:
    package_id: str = str(uuid4())
    CDPH_VR_FORMTYPE: str = "WILDFIRE"
    WildfireName: Optional[str] = random.choice(["Eaton Fire", "Palisades Fire"])
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


class PackageTask(Task):
    group = "vital-records"
    name = "package"

    def __init__(self, requestor_email: str):
        super().__init__(requestor_email=requestor_email)

    def handler(self, requestor_email: str):
        logger.debug(f"Creating request package for: {requestor_email}")

        package = Package(RequestorEmail=requestor_email)
        package_data = package.dict()

        reader = PdfReader(TEMPLATE)
        writer = PdfWriter()

        writer.append(reader)
        writer.update_page_form_field_values(writer.pages[0], package_data, auto_regenerate=False)

        filename = os.path.join(settings.STORAGE_DIR, f"vital-records-{package.package_id}.pdf")
        with open(filename, "wb") as output_stream:
            writer.write(output_stream)

        return filename

    def post_handler(self, package_task):
        requestor_email = package_task.kwargs.get("requestor_email")
        if package_task.success:
            logger.debug(f"Sending request package for: {requestor_email}")
            email_task = EmailTask(requestor_email, package_task.result)
            email_task.run()
        else:
            logger.error(f"Package creation failed for: {requestor_email}")


class EmailTask(Task):
    group = "vital-records"
    name = "email"

    def __init__(self, requestor_email: str, package: str):
        super().__init__(
            subject="Vital records request",
            body="A new request is attached.",
            requestor_email=requestor_email,
            package=package,
        )

    def handler(self, subject: str, body: str, requestor_email: str, package: str):
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email="noreply@example.gov",
            to=["records@example.gov"],
            cc=[requestor_email],
        )
        email.attach_file(package, "application/pdf")

        return email.send()
