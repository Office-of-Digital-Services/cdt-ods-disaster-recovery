import logging

from django.contrib import admin

from web.core import models

logger = logging.getLogger(__name__)


@admin.register(models.UserFlow)
class UserFlowAdmin(admin.ModelAdmin):
    list_display = ("label", "scopes", "eligibility_claim", "oauth_config")
