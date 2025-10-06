from django.urls import reverse

import pytest

from web.vital_records.models import VitalRecordsRequest
from web.vital_records.views import common
from web.vital_records.forms.common import EligibilityForm
from web.vital_records.session import Session


@pytest.fixture
def mock_Session_cls(mocker):
    session = mocker.Mock(spec=Session)
    return mocker.patch("web.vital_records.views.common.Session", return_value=session)


@pytest.mark.django_db
class TestIndexView:
    @pytest.fixture
    def view(self, app_request):
        v = common.IndexView()
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
        v = common.LoginView()
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
        v = common.StartView()
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


@pytest.mark.django_db
class TestStatementView:
    @pytest.fixture
    def view(self, app_request):
        v = common.StatementView()
        v.setup(app_request)
        return v

    @pytest.mark.parametrize(
        "record_type,expected_authorized_copy_explanation",
        [
            ("birth",  "To get an authorized copy, you must be the person named on the record or someone legally allowed to "
             "request it — like a parent, guardian, child, sibling, grandparent or spouse."),
            ("marriage", "To get an authorized copy, you must be the person named on the record or someone legally allowed to "
             "request it — like a parent, guardian, child, sibling, grandparent or spouse."),
            ("death", "To get an authorized copy, you must be the individual legally authorized to make this request — like a "
                "parent, guardian, child, sibling, grandparent or spouse."),
        ],
    )
    def test_get_context_data(self, view, record_type, expected_authorized_copy_explanation):
        view.object = VitalRecordsRequest(type=record_type)
        context = view.get_context_data()

        assert context["authorized_copy_explanation"] == expected_authorized_copy_explanation
        assert context["page_title"] == f"Replacement {record_type} record"


@pytest.mark.django_db
class TestSubmitView:
    @pytest.fixture
    def view(self, app_request):
        v = common.SubmitView()
        v.setup(app_request)
        return v

    @pytest.mark.parametrize(
        "record_type,expected_first_sentence",
        [
            ("birth", "The following information will be used to search for your replacement record."),
            ("marriage", "This is the information that will be used to search for the replacement marriage record."),
            ("death", "This is the information that will be used to search for the replacement death record."),
        ],
    )
    def test_get_context_data(self, view, record_type, expected_first_sentence):
        view.object = VitalRecordsRequest(type=record_type)
        context = view.get_context_data()

        assert context["first_sentence"] == expected_first_sentence
        assert "type" in context
        assert "county_display" in context
        assert context["details_include"] == f"vital_records/_confirm_{record_type}_details.html"


class TestSubmittedView:
    @pytest.fixture
    def view(app_request):
        v = common.SubmittedView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "vital_records/submitted.html"


class TestUnverifiedView:
    @pytest.fixture
    def view(app_request):
        v = common.UnverifiedView()
        v.setup(app_request)
        return v

    def test_template_name(self, view):
        assert view.template_name == "vital_records/unverified.html"
