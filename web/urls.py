"""
Django URL configuration for Digital Disaster Recovery Center (DDRC) project.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("web.core.urls")),
    path("admin/", admin.site.urls),
    path("oauth/", include("web.oauth.urls")),
    path("vitals/", include("web.vitals.urls")),
]
