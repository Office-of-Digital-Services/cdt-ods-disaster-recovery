from django.urls import reverse

import pytest

from web.vital_records import views
from web.vital_records.forms.common import EligibilityForm
from web.vital_records.session import Session


@pytest.fixture
def mock_Session_cls(mocker):
    session = mocker.Mock(spec=Session)
    return mocker.patch("web.vital_records.views.Session", return_value=session)


@pytest.mark.django_db
class TestIndexView:
    @pytest.fixture
    def view(self, app_request):
        v = views.IndexView()
        v.setup(app_request)
        return v

    def test_get_creates_new_session(self, view, app_request, mock_Session_cls):
        view.get(app_request)

        mock_Session_cls.assert_called_once_with(app_request, reset=True)

    def test_template_name(self, view):
        assert view.template_name == "vital_records/index.html"


@pytest.mark.django_db
class TestLoginView:
    @pytest.fixture
    def view(self, app_request):
        v = views.LoginView()
        v.setup(app_request)
        return v

    def test_dispatch_creates_new_session(self, view, app_request, mock_Session_cls):
        view.dispatch(app_request)

        mock_Session_cls.assert_called_once_with(app_request, reset=True)

    def test_dispatch_redirects_to_login(self, view, app_request):
        response = view.dispatch(app_request)

        assert response.status_code == 302
        assert response.url == reverse("cdt:login")


@pytest.mark.django_db
class TestStartView:
    @pytest.fixture
    def view(self, app_request):
        v = views.StartView()
        v.setup(app_request)
        return v

    @pytest.fixture
    def form(self, mocker, request_id):
        frm = mocker.Mock(spec=EligibilityForm)
        # mock the model/return value of calling form.save()
        obj = frm.save.return_value
        # set the model's ID
        obj.pk = request_id

        return frm

    def test_form_valid(self, app_request, request_id, view, form, mock_Session_cls):
        response = view.form_valid(form)
        # Session was initialized with the request_id
        mock_Session_cls.assert_called_once_with(app_request, request_id=request_id)
        # response is a redirect
        assert response.status_code == 302
        assert response.url == f"/vital-records/request/{request_id}/type"


class TestSubmittedView:
    @pytest.fixture
    def view(app_request):
        v = views.SubmittedView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "vital_records/submitted.html"


class TestUnverifiedView:
    @pytest.fixture
    def view(app_request):
        v = views.UnverifiedView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "vital_records/unverified.html"
