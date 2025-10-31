import datetime
import pytest

from web.vital_records.forms.common import DateForm, DateOfBirthForm, DateOfEventForm, StatementForm, TypeForm
from web.vital_records.models import VitalRecordsRequest


@pytest.mark.django_db
class TestTypeForm:
    def test_type_choices(self):
        form = TypeForm()

        assert form.fields["type"].choices == [
            ("", "Select type"),
            ("birth", "Birth record"),
            ("marriage", "Marriage record"),
            ("death", "Death record"),
        ]

    def test_save_type_changed(self):
        # Simulate that a user had started filling out a VitalRecordsRequest instance.
        existing_instance = VitalRecordsRequest.objects.create(
            fire="eaton",
            type="birth",
            relationship="self",
            legal_attestation="Test User",
            first_name="First",
            middle_name="Middle",
            last_name="Last",
            county_of_event="Los Angeles",
            date_of_birth=datetime.datetime(1990, 9, 22, 19, 17, 58, tzinfo=datetime.UTC),
            date_of_event=datetime.datetime(1990, 9, 22, 19, 17, 58, tzinfo=datetime.UTC),
            person_1_first_name="First1",
            person_1_middle_name="Middle1",
            person_1_last_name="Last1",
            person_2_first_name="First2",
            person_2_middle_name="Middle2",
            person_2_last_name="Last2",
            order_first_name="Requester",
            order_last_name="Person",
            address="123 Main St",
            address_2="Apt 4A",
            city="Los Angeles",
            state="CA",
            zip_code="90012",
            email_address="test@example.com",
            phone_number="3231234567",
        )
        existing_instance.save()

        # Then, simulate changing the type.
        form = TypeForm(data={"type": "death"}, instance=existing_instance)
        form.save()

        assert existing_instance.status == "initialized"
        assert existing_instance.fire == "eaton"
        assert existing_instance.type == "death"
        assert existing_instance.relationship == ""
        assert existing_instance.legal_attestation == ""
        assert existing_instance.first_name == ""
        assert existing_instance.middle_name == ""
        assert existing_instance.last_name == ""
        assert existing_instance.county_of_event == ""
        assert existing_instance.date_of_birth is None
        assert existing_instance.date_of_event is None
        assert existing_instance.person_1_first_name == ""
        assert existing_instance.person_1_middle_name == ""
        assert existing_instance.person_1_last_name == ""
        assert existing_instance.person_1_birth_last_name == ""
        assert existing_instance.person_2_first_name == ""
        assert existing_instance.person_2_middle_name == ""
        assert existing_instance.person_2_last_name == ""
        assert existing_instance.person_2_birth_last_name == ""
        assert existing_instance.order_first_name == ""
        assert existing_instance.order_last_name == ""
        assert existing_instance.address == ""
        assert existing_instance.address_2 == ""
        assert existing_instance.city == ""
        assert existing_instance.state == ""
        assert existing_instance.zip_code == ""
        assert existing_instance.email_address == ""
        assert existing_instance.phone_number == ""

    def test_save_type_unchanged(self):
        # Simulate that a user had started filling out a VitalRecordsRequest instance.
        existing_instance = VitalRecordsRequest.objects.create(
            fire="eaton",
            type="birth",
            relationship="self",
            legal_attestation="Test User",
            first_name="First",
            middle_name="Middle",
            last_name="Last",
            county_of_event="Los Angeles",
            date_of_birth=datetime.datetime(1990, 9, 22, 19, 17, 58, tzinfo=datetime.UTC),
            date_of_event=datetime.datetime(1990, 9, 22, 19, 17, 58, tzinfo=datetime.UTC),
            person_1_first_name="First1",
            person_1_middle_name="Middle1",
            person_1_last_name="Last1",
            person_2_first_name="First2",
            person_2_middle_name="Middle2",
            person_2_last_name="Last2",
            order_first_name="Requester",
            order_last_name="Person",
            address="123 Main St",
            address_2="Apt 4A",
            city="Los Angeles",
            state="CA",
            zip_code="90012",
            email_address="test@example.com",
            phone_number="3231234567",
        )
        existing_instance.save()

        # Then, simulate going back to the form and not changing the type.
        form = TypeForm(data={"type": "birth"}, instance=existing_instance)
        form.save()

        assert existing_instance.status == "initialized"
        assert existing_instance.fire == "eaton"
        assert existing_instance.type == "birth"
        assert existing_instance.relationship == "self"
        assert existing_instance.legal_attestation == "Test User"
        assert existing_instance.first_name == "First"
        assert existing_instance.middle_name == "Middle"
        assert existing_instance.last_name == "Last"
        assert existing_instance.county_of_event == "Los Angeles"
        assert existing_instance.date_of_birth == datetime.datetime(1990, 9, 22, 19, 17, 58, tzinfo=datetime.UTC)
        assert existing_instance.date_of_event == datetime.datetime(1990, 9, 22, 19, 17, 58, tzinfo=datetime.UTC)
        assert existing_instance.person_1_first_name == "First1"
        assert existing_instance.person_1_middle_name == "Middle1"
        assert existing_instance.person_1_last_name == "Last1"
        assert existing_instance.person_2_first_name == "First2"
        assert existing_instance.person_2_middle_name == "Middle2"
        assert existing_instance.person_2_last_name == "Last2"
        assert existing_instance.order_first_name == "Requester"
        assert existing_instance.order_last_name == "Person"
        assert existing_instance.address == "123 Main St"
        assert existing_instance.address_2 == "Apt 4A"
        assert existing_instance.city == "Los Angeles"
        assert existing_instance.state == "CA"
        assert existing_instance.zip_code == "90012"
        assert existing_instance.email_address == "test@example.com"
        assert existing_instance.phone_number == "3231234567"


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
