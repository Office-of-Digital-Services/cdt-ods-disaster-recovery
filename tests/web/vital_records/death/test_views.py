import pytest

from web.vital_records.forms.death import SpouseNameForm
from web.vital_records.models import VitalRecordsRequest
from web.vital_records.views.death import DateOfDeathView, SpouseView


@pytest.mark.django_db
class TestDateOfDeathView:
    @pytest.fixture
    def view(self, app_request):
        v = DateOfDeathView()
        v.request = app_request
        v.object = VitalRecordsRequest(type="death")
        return v

    def test_get_context_data(self, view):
        context = view.get_context_data()

        assert context["form_layout"] == "date_form"
        assert context["form_hint_name"] == "death-date-hint"
        assert context["form_question"] == "What was the date of death?"
        assert context["form_hint"] == "If you’re not sure, enter their approximate date of death."


@pytest.mark.django_db
class TestSpouseView:
    @pytest.fixture
    def view(self, app_request):
        v = SpouseView()
        v.request = app_request
        v.object = VitalRecordsRequest(type="death")
        return v

    def test_get_context_data(self, view):
        context = view.get_context_data()

        assert context["form_question"] == "What was the full name of the deceased person’s spouse or domestic partner?"
        assert isinstance(context["form"], SpouseNameForm)

        form = context["form"]
        expected_fields = [
            form["person_2_first_name"],
            form["person_2_middle_name"],
            form["person_2_last_name"],
        ]
        assert context["form_fields"] == expected_fields
