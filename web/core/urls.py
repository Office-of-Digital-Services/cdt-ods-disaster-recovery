from django.urls import path
from django.views.generic import TemplateView

app_name = "core"

# /
urlpatterns = [
    path("", TemplateView.as_view(template_name="core/index.html"), name="index"),
    path("logout/complete", TemplateView.as_view(template_name="core/post_logout.html"), name="post_logout"),
]
