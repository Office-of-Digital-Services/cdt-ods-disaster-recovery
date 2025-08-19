from django.urls import reverse
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
        v.object = models.VitalRecordsRequest(type="birth")
        return v

    @pytest.fixture
    def marriage_view(self, app_request):
        v = self.SampleView()
        v.setup(app_request)
        v.object = models.VitalRecordsRequest(type="marriage")
        return v

    @pytest.mark.parametrize(
        "step_name,expected_step_number,expected_previous_route",
        [
            (Steps.name, 1, Routes.request_statement),
            (Steps.county_of_birth, 2, Routes.birth_request_name),
            (Steps.date_of_birth, 3, Routes.birth_request_county),
            (Steps.parents_names, 4, Routes.birth_request_dob),
            (Steps.order_information, 5, Routes.birth_request_parents),
            (Steps.preview_and_submit, 6, Routes.request_order),
        ],
    )
    def test_get_context_data_birth(self, birth_view, step_name, expected_step_number, expected_previous_route):
        birth_view.step_name = step_name
        context = birth_view.get_context_data()

        assert context["page_title"] == "Replacement birth record"
        assert context["all_steps"] == [
            Steps.name,
            Steps.county_of_birth,
            Steps.date_of_birth,
            Steps.parents_names,
            Steps.order_information,
            Steps.preview_and_submit,
        ]
        assert context["step_number"] == expected_step_number
        assert context["previous_route"] == Routes.app_route(expected_previous_route)

    @pytest.mark.parametrize(
        "step_name,expected_step_number,expected_previous_route",
        [
            (Steps.name, 1, Routes.request_statement),
            (Steps.county_of_marriage, 2, Routes.marriage_request_name),
            (Steps.date_of_marriage, 3, Routes.marriage_request_county),
            (Steps.order_information, 4, Routes.marriage_request_date),
            (Steps.preview_and_submit, 5, Routes.request_order),
        ],
    )
    def test_get_context_data_marriage(self, marriage_view, step_name, expected_step_number, expected_previous_route):
        marriage_view.step_name = step_name
        context = marriage_view.get_context_data()

        assert context["page_title"] == "Replacement marriage record"
        assert context["all_steps"] == [
            Steps.name,
            Steps.county_of_marriage,
            Steps.date_of_marriage,
            Steps.order_information,
            Steps.preview_and_submit,
        ]
        assert context["step_number"] == expected_step_number
        assert context["previous_route"] == Routes.app_route(expected_previous_route)

    @pytest.mark.parametrize(
        "step_name,expected_next_route",
        [
            (Steps.name, Routes.birth_request_county),
            (Steps.county_of_birth, Routes.birth_request_dob),
            (Steps.date_of_birth, Routes.birth_request_parents),
            (Steps.parents_names, Routes.request_order),
            (Steps.order_information, Routes.request_submit),
            (Steps.preview_and_submit, Routes.request_submitted),
        ],
    )
    def test_get_success_url_birth(self, birth_view, step_name, expected_next_route):
        birth_view.step_name = step_name
        success_url = birth_view.get_success_url()
        next_route = Routes.app_route(expected_next_route)

        assert success_url == reverse(next_route, kwargs={"pk": birth_view.object.pk})

    @pytest.mark.skip(reason="reverse will return an error until marriage URLs are defined")
    @pytest.mark.parametrize(
        "step_name,expected_next_route",
        [
            (Steps.name, Routes.marriage_request_county),
            (Steps.county_of_marriage, Routes.marriage_request_date),
            (Steps.date_of_marriage, Routes.request_order),
            (Steps.order_information, Routes.request_submit),
            (Steps.preview_and_submit, Routes.request_submitted),
        ],
    )
    def test_get_success_url_marriage(self, marriage_view, step_name, expected_next_route):
        marriage_view.step_name = step_name
        success_url = marriage_view.get_success_url()
        next_route = Routes.app_route(expected_next_route)

        assert success_url == reverse(next_route, kwargs={"pk": marriage_view.object.pk})
