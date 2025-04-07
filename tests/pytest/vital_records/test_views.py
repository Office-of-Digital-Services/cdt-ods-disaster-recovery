import pytest

from web.vital_records import views
from web.vital_records.session import Session


@pytest.fixture
def mock_Session_cls(mocker):
    session = mocker.Mock(spec=Session)
    return mocker.patch("web.vital_records.views.Session", return_value=session)


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


class TestRequestView:
    @pytest.fixture
    def view(app_request):
        v = views.RequestView()
        v.setup(app_request)
        return v

    def test_get_context_data(self, view, mock_Session_cls):
        mock_Session_cls.return_value.verified_email = "test@example.com"

        context = view.get_context_data()

        assert context["email"] == "test@example.com"

    def test_template_name(self, view):
        assert view.template_name == "vital_records/request.html"


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
