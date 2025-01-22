"""
Django URL configuration for Digital Disaster Recovery Center (DDRC) project.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
