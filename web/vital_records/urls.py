from django.urls import path

from web.vital_records import views

app_name = "vital_records"

# /vital-records
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("login", views.LoginView.as_view(), name="login"),
    path("request", views.RequestView.as_view(), name="request"),
    path("submitted", views.SubmittedView.as_view(), name="submitted"),
    path("unverified", views.UnverifiedView.as_view(), name="unverified"),
]
