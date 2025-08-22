import logging
import os

from django.conf import settings

from web.vital_records.models import VitalRecordsRequest

logger = logging.getLogger(__name__)


def get_package_filename(request: VitalRecordsRequest) -> str:
    return os.path.join(
        settings.STORAGE_DIR, f"vital-records-{request.submitted_at.strftime("%Y-%m-%d")}-{request.type}-{request.id}.pdf"
    )
