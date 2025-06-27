from django.urls import path
from django.views.generic import RedirectView, TemplateView

from web.vital_records.routes import Routes

app_name = "core"

# /
urlpatterns = [
    path("", RedirectView.as_view(pattern_name=Routes.app_route(Routes.index)), name="index"),
    path("logout/complete", TemplateView.as_view(template_name="core/post_logout.html"), name="post_logout"),
]
