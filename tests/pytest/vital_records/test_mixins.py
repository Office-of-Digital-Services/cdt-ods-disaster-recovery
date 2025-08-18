from django.views import View

import pytest

from web.vital_records import models
from web.vital_records.mixins import Steps, StepsMixin, ValidateRequestIdMixin
from web.vital_records.routes import Routes
from web.vital_records.session import Session


@pytest.mark.django_db
class TestValidateRequestIdMixin:
    class SampleView(ValidateRequestIdMixin, View):
        def get(self, request, *args, **kwargs):
            return "Success"

    @pytest.fixture
    def view(self, app_request):
        v = self.SampleView()
        v.setup(app_request)
        return v

    @pytest.fixture(autouse=True)
    def session(self, app_request, request_id):
        return Session(app_request, request_id)

    def test_dispatch_without_valid_request_id(self, view, app_request):
        response = view.dispatch(app_request)

        assert response.status_code == 403

    def test_dispatch_with_valid_request_id(self, view, app_request, request_id):
        view.kwargs = {"pk": request_id}

        response = view.dispatch(app_request)

        assert response == "Success"


@pytest.mark.django_db
class TestStepsMixin:
    class SampleView(StepsMixin, View):
        pass

    @pytest.fixture
    def birth_view(self, app_request):
        v = self.SampleView()
        v.setup(app_request)
        v.step_name = Steps.name
        v.object = models.VitalRecordsRequest(type="birth")
        return v

    @pytest.fixture
    def marriage_view(self, app_request):
        v = self.SampleView()
        v.setup(app_request)
        v.step_name = Steps.name
        v.object = models.VitalRecordsRequest(type="marriage")
        return v

    def test_get_context_data_birth(self, birth_view):
        context = birth_view.get_context_data()

        assert context["all_steps"] == [
            Steps.name,
            Steps.county_of_birth,
            Steps.date_of_birth,
            Steps.parents_names,
            Steps.order_information,
            Steps.preview_and_submit,
        ]

        assert context["step_number"] == 1  # since fixture's step_name is "Name"
        assert context["previous_route"] == Routes.app_route(Routes.request_statement)

    def test_get_context_data_marriage(self, marriage_view):
        context = marriage_view.get_context_data()

        assert context["all_steps"] == [
            Steps.name,
            Steps.county_of_marriage,
            Steps.date_of_marriage,
            Steps.order_information,
            Steps.preview_and_submit,
        ]

        assert context["step_number"] == 1  # since fixture's step_name is "Name"
        assert context["previous_route"] == Routes.app_route(Routes.request_statement)
