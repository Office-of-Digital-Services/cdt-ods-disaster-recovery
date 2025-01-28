"""
Django WSGI config.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import logging
import os

from django.core.wsgi import get_wsgi_application
from django.urls import include, path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")

logger = logging.getLogger(__name__)
application = get_wsgi_application()

try:
    import web.urls
    from web.core.models import UserFlow

    for flow in UserFlow.objects.all():
        web.urls.urlpatterns.append(path(f"{flow.system_name}/", include(flow.urlconf_path)))
except Exception as ex:
    logger.error(ex)
