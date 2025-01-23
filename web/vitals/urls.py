from django.urls import path
from django.views.generic import TemplateView

app_name = "vitals"

# /vitals
urlpatterns = [path("", TemplateView.as_view(template_name="vitals/index.html"), name="index")]
