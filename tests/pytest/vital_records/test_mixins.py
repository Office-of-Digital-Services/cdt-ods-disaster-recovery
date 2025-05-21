from django.views import View

import pytest

from web.vital_records.mixins import ValidateRequestIdMixin
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
