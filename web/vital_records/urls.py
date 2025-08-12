from django.urls import path

from web.vital_records import views

# the `app_name` import isn't used directly, but the symbol still needs to be defined in this module
from web.vital_records.routes import app_name, Routes  # noqa: F401

# /vital-records
urlpatterns = [
    path("", views.IndexView.as_view(), name=Routes.index),
    path("login", views.LoginView.as_view(), name=Routes.login),
    path("request", views.StartView.as_view(), name=Routes.request_start),
    path("request/<uuid:pk>/type", views.TypeView.as_view(), name=Routes.request_type),
    path("request/<uuid:pk>/statement", views.StatementView.as_view(), name=Routes.request_statement),
    path("request/<uuid:pk>/name", views.NameView.as_view(), name=Routes.request_name),
    path("request/<uuid:pk>/county", views.CountyView.as_view(), name=Routes.request_county),
    path("request/<uuid:pk>/dob", views.DateOfBirthView.as_view(), name=Routes.request_dob),
    path("request/<uuid:pk>/parents", views.ParentsNamesView.as_view(), name=Routes.request_parents),
    path("request/<uuid:pk>/order", views.OrderInfoView.as_view(), name=Routes.request_order),
    path("request/<uuid:pk>/submit", views.SubmitView.as_view(), name=Routes.request_submit),
    path("request/<uuid:pk>", views.SubmittedView.as_view(), name=Routes.request_submitted),
    path("unverified", views.UnverifiedView.as_view(), name=Routes.unverified),
]
