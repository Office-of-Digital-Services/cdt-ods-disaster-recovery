import logging

from django.conf import settings
from django.contrib import admin

import requests

from web.core import models

GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

logger = logging.getLogger(__name__)


@admin.register(models.UserFlow)
class UserFlowAdmin(admin.ModelAdmin):
    list_display = ("system_name", "oauth_config", "claims_request")


def pre_login_user(user, request):
    logger.debug(f"Running pre-login callback for user: {user.username}")
    token = request.session.get("google_sso_access_token")
    if token:
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # Request Google user info to get name and email
        response = requests.get(GOOGLE_USER_INFO_URL, headers=headers, timeout=settings.REQUESTS_TIMEOUT)
        user_data = response.json()
        logger.debug(f"Updating user data from Google for user with email: {user_data['email']}")

        user.first_name = user_data["given_name"]
        user.last_name = user_data["family_name"]
        user.username = user_data["email"]
        user.email = user_data["email"]
        user.save()
    else:
        logger.warning("google_sso_access_token not found in session.")
