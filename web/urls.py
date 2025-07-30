"""
Django root URL configuration.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

import logging

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

from web.vital_records.hooks import VitalRecordsHooks

logger = logging.getLogger(__name__)

# /
urlpatterns = [
    path("", include("web.core.urls")),
    path("admin/", admin.site.urls),
    path("google_sso/", include("django_google_sso.urls", namespace="django_google_sso")),
    path("oauth/", include("cdt_identity.urls"), {"hooks": VitalRecordsHooks}),
    path("vital-records/", include("web.vital_records.urls")),
]

# register view handlers for debugging
if settings.DEBUG:

    def debug_error(request):
        logger.error("Debug error")
        return HttpResponse("Debug error was logged")

    def debug_exception(request):
        raise RuntimeError("Debug exception")

    urlpatterns.append(path("error", debug_error))
    urlpatterns.append(path("exception", debug_exception))
