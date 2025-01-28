from django.urls import path

from web.vital_records import views

app_name = "vital_records"

# /vital-records
urlpatterns = [
    path("", views.index, name="index"),
    path("request", views.request, name="request"),
    path("submitted", views.submitted, name="submitted"),
    path("unverified", views.unverified, name="unverified"),
]
