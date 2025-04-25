from django.views import View

import pytest

from web.core.views import EligibilityMixin


class SampleView(EligibilityMixin, View):
    pass


class TestEligibilityMixin:

    @pytest.fixture
    def view(self, app_request):
        v = SampleView()
        v.setup(app_request)
        return v

    def test_dispatch_without_verified_eligibility(self, view, app_request, mocker):
        """Test EligibilityMixin redirects when eligibility is not verified"""
        mock_session = mocker.patch("web.core.views.Session")
        mock_session.return_value.has_verified_eligibility.return_value = False

        response = view.dispatch(app_request)

        assert response.status_code == 302
        assert response.url == "/vital-records/login"

    def test_dispatch_with_verified_eligibility(self, view, app_request, mocker):
        """Test EligibilityMixin allows dispatch when eligibility is verified"""
        mock_session = mocker.patch("web.core.views.Session")
        mock_session.return_value.has_verified_eligibility.return_value = True

        view.dispatch(app_request)

        mock_session.assert_called_once_with(app_request)
        mock_session.return_value.has_verified_eligibility.assert_called_once()
