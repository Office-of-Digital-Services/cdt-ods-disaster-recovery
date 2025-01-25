from django.urls import path
from django.views.generic import TemplateView

app_name = "vital_records"

# /vital-records
urlpatterns = [path("", TemplateView.as_view(template_name="vital_records/index.html"), name="index")]
