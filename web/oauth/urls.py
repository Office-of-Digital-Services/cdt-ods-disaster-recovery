from django.urls import path
from django.views.generic import TemplateView

from . import views


app_name = "oauth"
endpoints_template = [
    "cancel",
    "error",
    "post_logout",
    "success",
]
endpoints_view = [
    "authorize",
    "login",
    "logout",
]

# /oauth
urlpatterns = []

for endpoint in endpoints_template:
    # simple template-only view
    urlpatterns.append(path(endpoint, TemplateView.as_view(template_name=f"oauth/{endpoint}.html"), name=endpoint))
for endpoint in endpoints_view:
    # view function implementation
    urlpatterns.append(path(endpoint, getattr(views, endpoint), name=endpoint))
