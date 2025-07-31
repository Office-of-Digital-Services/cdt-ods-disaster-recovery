import logging
import os
from uuid import UUID

from django.conf import settings

logger = logging.getLogger(__name__)


def get_package_filename(request_id: UUID) -> str:
    return os.path.join(settings.STORAGE_DIR, f"vital-records-{request_id}.pdf")
