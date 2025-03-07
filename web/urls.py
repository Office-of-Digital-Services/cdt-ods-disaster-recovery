"""
Django root URL configuration.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("web.core.urls")),
    path("admin/", admin.site.urls),
    path("oauth/", include("web.oauth.urls")),
]
