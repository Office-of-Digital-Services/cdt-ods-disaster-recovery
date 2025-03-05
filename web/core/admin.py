import logging

from django.contrib import admin

from web.core import models

logger = logging.getLogger(__name__)


@admin.register(models.UserFlow)
class UserFlowAdmin(admin.ModelAdmin):
    list_display = ("system_name", "oauth_config", "claims_request")
