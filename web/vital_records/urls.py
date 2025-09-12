from django.urls import path

from web.vital_records.views import birth, common, death, marriage

# the `app_name` import isn't used directly, but the symbol still needs to be defined in this module
from web.vital_records.routes import app_name, Routes  # noqa: F401

# /vital-records
urlpatterns = [
    # common URLs
    path("", common.IndexView.as_view(), name=Routes.index),
    path("login", common.LoginView.as_view(), name=Routes.login),
    path("request", common.StartView.as_view(), name=Routes.request_start),
    path("request/<uuid:pk>/type", common.TypeView.as_view(), name=Routes.request_type),
    path("request/<uuid:pk>/statement", common.StatementView.as_view(), name=Routes.request_statement),
    # birth flow URLs
    path("request/birth/<uuid:pk>/name", birth.NameView.as_view(), name=Routes.birth_request_name),
    path("request/birth/<uuid:pk>/county", birth.CountyView.as_view(), name=Routes.birth_request_county),
    path("request/birth/<uuid:pk>/dob", birth.DateOfBirthView.as_view(), name=Routes.birth_request_dob),
    path("request/birth/<uuid:pk>/parents", birth.ParentsNamesView.as_view(), name=Routes.birth_request_parents),
    # marriage flow URLs
    path("request/marriage/<uuid:pk>/name", marriage.NameView.as_view(), name=Routes.marriage_request_name),
    path("request/marriage/<uuid:pk>/county", marriage.CountyView.as_view(), name=Routes.marriage_request_county),
    path("request/marriage/<uuid:pk>/date", marriage.DateOfMarriageView.as_view(), name=Routes.marriage_request_date),
    # death flow URLs
    path("request/death/<uuid:pk>/name", death.NameView.as_view(), name=Routes.death_request_name),
    path("request/death/<uuid:pk>/county", death.CountyView.as_view(), name=Routes.death_request_county),
    path("request/death/<uuid:pk>/date", death.DateOfDeathView.as_view(), name=Routes.death_request_date),
    path("request/death/<uuid:pk>/dob", death.DateOfBirthView.as_view(), name=Routes.death_request_dob),
    path("request/death/<uuid:pk>/parent", death.ParentView.as_view(), name=Routes.death_request_parent),
    path("request/death/<uuid:pk>/spouse", death.SpouseView.as_view(), name=Routes.death_request_spouse),
    # remaining common URLs
    path("request/<uuid:pk>/order", common.OrderInfoView.as_view(), name=Routes.request_order),
    path("request/<uuid:pk>/submit", common.SubmitView.as_view(), name=Routes.request_submit),
    path("request/<uuid:pk>", common.SubmittedView.as_view(), name=Routes.request_submitted),
    path("unverified", common.UnverifiedView.as_view(), name=Routes.unverified),
]
