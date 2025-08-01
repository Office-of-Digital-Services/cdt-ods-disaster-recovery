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

    def handler(self, request_id: UUID, package: str):
        logger.debug(f"Sending request package for: {request_id}")
        request = VitalRecordsRequest.get_with_status(request_id, "packaged")

        context = {
            "number_of_copies": request.number_of_records,
            "logo_url": "https://webstandards.ca.gov/wp-content/uploads/sites/8/2024/10/cagov-logo-coastal-flat.png",
            "email_address": request.email_address,
        }
        text_content = render_to_string(EMAIL_TXT_TEMPLATE, context)
        html_content = render_to_string(EMAIL_HTML_TEMPLATE, context)
        email = EmailMultiAlternatives(
            subject="Completed: Birth Record Request",
            body=text_content,
            to=[settings.VITAL_RECORDS_EMAIL_TO],
        )
        email.attach_alternative(html_content, "text/html")
        email.attach_file(package, "application/pdf")
        result = email.send()

        request.complete_send()
        request.finish()
        request.save()

        logger.debug(f"Request package sent for: {request_id} with response {result}")

        return result
