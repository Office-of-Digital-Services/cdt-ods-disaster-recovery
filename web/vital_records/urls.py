from django.urls import path

from web.vital_records.views import common

# the `app_name` import isn't used directly, but the symbol still needs to be defined in this module
from web.vital_records.routes import app_name, Routes  # noqa: F401

# /vital-records
urlpatterns = [
    path("", common.IndexView.as_view(), name=Routes.index),
    path("login", common.LoginView.as_view(), name=Routes.login),
    path("request", common.StartView.as_view(), name=Routes.request_start),
    path("request/<uuid:pk>/type", common.TypeView.as_view(), name=Routes.request_type),
    path("request/<uuid:pk>/statement", common.StatementView.as_view(), name=Routes.request_statement),
    path("request/birth/<uuid:pk>/name", common.NameView.as_view(), name=Routes.birth_request_name),
    path("request/birth/<uuid:pk>/county", common.CountyView.as_view(), name=Routes.birth_request_county),
    path("request/birth/<uuid:pk>/dob", common.DateOfBirthView.as_view(), name=Routes.birth_request_dob),
    path("request/birth/<uuid:pk>/parents", common.ParentsNamesView.as_view(), name=Routes.birth_request_parents),
    path("request/<uuid:pk>/order", common.OrderInfoView.as_view(), name=Routes.request_order),
    path("request/<uuid:pk>/submit", common.SubmitView.as_view(), name=Routes.request_submit),
    path("request/<uuid:pk>", common.SubmittedView.as_view(), name=Routes.request_submitted),
    path("unverified", common.UnverifiedView.as_view(), name=Routes.unverified),
]
