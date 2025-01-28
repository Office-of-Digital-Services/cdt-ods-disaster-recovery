"""
Django WSGI config.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.urls import include, path


from web.core.models import UserFlow
import web.urls

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")

application = get_wsgi_application()

for flow in UserFlow.objects.all():
    web.urls.urlpatterns.append(path(f"{flow.system_name}/", include(flow.urlconf_path)))
