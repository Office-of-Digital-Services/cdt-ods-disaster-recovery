import datetime
import pytest

from web.vital_records.forms.common import DateForm, DateOfBirthForm, DateOfEventForm, StatementForm, TypeForm
from web.vital_records.models import VitalRecordsRequest


def test_TypeForm():
    form = TypeForm()

    assert form.fields["type"].choices == [
        ("", "Select type"),
        ("birth", "Birth record"),
        ("marriage", "Marriage record"),
        ("death", "Death record"),
    ]


@pytest.mark.parametrize(
    "type,expected_choices",
    [
        (
            "birth",
            [
                ("", "Select relationship"),
                ("self", "Self"),
                ("parent", "Parent"),
                ("legal guardian", "Legal guardian"),
                ("child", "Child"),
                ("grandparent", "Grandparent"),
                ("grandchild", "Grandchild"),
                ("sibling", "Sibling"),
                ("spouse", "Spouse"),
                ("domestic_partner", "Domestic partner"),
            ],
        ),
        (
            "marriage",
            [
                ("", "Select relationship"),
                ("self", "Self"),
                ("parent", "Parent"),
                ("legal guardian", "Legal guardian"),
                ("child", "Child"),
                ("grandparent", "Grandparent"),
                ("grandchild", "Grandchild"),
                ("sibling", "Sibling"),
                ("spouse", "Spouse"),
                ("domestic_partner", "Domestic partner"),
            ],
        ),
        (
            "death",
            [
                ("", "Select relationship"),
                ("parent", "Parent"),
                ("legal guardian", "Legal guardian"),
                ("child", "Child"),
                ("grandparent", "Grandparent"),
                ("grandchild", "Grandchild"),
                ("sibling", "Sibling"),
                ("spouse", "Spouse"),
                ("domestic_partner", "Domestic partner"),
                ("surviving_next_of_kin", "Surviving next of kin (As specified in HSC § 7100)"),
            ],
        ),
    ],
)
def test_StatementForm(type, expected_choices):
    model_instance = VitalRecordsRequest(type=type)
    form = StatementForm(instance=model_instance)

    choices = form.fields["relationship"].choices
    assert choices == expected_choices


class TestDateForm:

    @pytest.fixture
    def valid_date(self):
        """Fixture to create a valid date dictionary."""
        return {"month": "9", "day": "22", "year": "1990"}

    def test_raises_not_implemented_error(self):
        with pytest.raises(NotImplementedError, match="'date_field_name' must be set on the subclass."):
            DateForm()

    def test__init__correct_data(self):
        event_date = datetime.datetime(1990, 9, 22, 19, 17, 58, tzinfo=datetime.UTC)
        model_instance = VitalRecordsRequest(date_of_event=event_date)
        form = DateOfEventForm(instance=model_instance)

        assert form.fields["month"].initial == 9
        assert form.fields["day"].initial == 22
        assert form.fields["year"].initial == 1990

    def test_clean_is_valid(self, valid_date):
        form = DateOfEventForm(data=valid_date)

        assert form.is_valid()
        assert form.cleaned_data["date_of_event"] == datetime.date(1990, 9, 22)

    def test_clean_is_invalid(self):
        form_data = {"month": "15", "day": "22", "year": "1990"}
        form = DateOfEventForm(data=form_data)

        assert not form.is_valid()

    @pytest.mark.parametrize(
        "form_class, date_field_name",
        [
            (DateOfEventForm, "date_of_event"),
            (DateOfBirthForm, "date_of_birth"),
        ],
    )
    @pytest.mark.django_db
    def test_save_date_of_event(self, form_class, date_field_name, valid_date):
        record = VitalRecordsRequest.objects.create(**{date_field_name: None})
        form = form_class(data=valid_date, instance=record)

        form.save(commit=True)

        expected_date = datetime.date(1990, 9, 22)
        assert getattr(record, date_field_name) == expected_date
