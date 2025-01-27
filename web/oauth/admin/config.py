import logging

from django.contrib import admin

from .. import models

logger = logging.getLogger(__name__)


@admin.register(models.ClientConfig)
class ClientConfigAdmin(admin.ModelAdmin):
    list_display = ("client_name", "authority", "scheme")
