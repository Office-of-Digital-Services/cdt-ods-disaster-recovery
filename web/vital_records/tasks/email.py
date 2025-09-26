import logging
from uuid import UUID

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from web.core.tasks import Task
from web.vital_records.models import VitalRecordsRequest

logger = logging.getLogger(__name__)

EMAIL_HTML_TEMPLATE = "vital_records/email.html"
EMAIL_TXT_TEMPLATE = EMAIL_HTML_TEMPLATE.replace(".html", ".txt")


class EmailTask(Task):
    group = "vital-records"
    name = "email"

    def __init__(self, request_id: UUID, package: str):
        super().__init__(request_id=request_id, package=package)

    def _format_record_type(self, record_type: str) -> str:
        """
        Checks the value of the record type and returns a
        string formatted for the email template.
        """
        type_format = {
            "birth": "Birth",
            "marriage": "Marriage",
            "death": "Death",
        }

        return type_format.get(record_type)

    def _create_base_email(
        self, subject: str, to_address: list[str], text_content: str, html_content: str
    ) -> EmailMultiAlternatives:
        """Helper method to create and configure a base email object."""
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=to_address,
        )
        email.attach_alternative(html_content, "text/html")
        return email

    def handler(self, request_id: UUID, package: str):
        logger.debug(f"Sending request package for: {request_id}")
        request = VitalRecordsRequest.get_with_status(request_id, "packaged")
        request_type = self._format_record_type(request.type)
        requestor_email_address = request.email_address

        context = {
            "number_of_copies": request.number_of_records,
            "logo_url": "https://webstandards.ca.gov/wp-content/uploads/sites/8/2024/10/cagov-logo-coastal-flat.png",
            "email_address": requestor_email_address,
            "request_type": request_type,
        }
        text_content = render_to_string(EMAIL_TXT_TEMPLATE, context)
        html_content = render_to_string(EMAIL_HTML_TEMPLATE, context)

        email_office = self._create_base_email(
            subject=f"Completed: {request_type} Record Request",
            to_address=[settings.VITAL_RECORDS_EMAIL_TO],
            text_content=text_content,
            html_content=html_content,
        )
        email_office.attach_file(package, "application/pdf")
        result_office = email_office.send()  # returns number of successfully sent emails

        email_requestor = self._create_base_email(
            subject=f"Completed: {request_type} Record Request",
            to_address=[requestor_email_address],
            text_content=text_content,
            html_content=html_content,
        )
        result_requestor = email_requestor.send()  # returns number of successfully sent emails

        request.complete_send()
        request.finish()
        request.save()

        logger.debug(f"Request package sent to CDPH for: {request_id} with response {result_office}")
        logger.debug(f"Request package sent to requestor for: {request_id} with response {result_requestor}")

        return (result_office, result_requestor)  # (1,1) is a successful task run
