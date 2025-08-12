import datetime
from django import forms

from web.vital_records.models import VitalRecordsRequest

MONTH_DISPLAY_CHOICES = [
    ("", "Select"),
    (1, "01 - January"),
    (2, "02 - February"),
    (3, "03 - March"),
    (4, "04 - April"),
    (5, "05 - May"),
    (6, "06 - June"),
    (7, "07 - July"),
    (8, "08 - August"),
    (9, "09 - September"),
    (10, "10 - October"),
    (11, "11 - November"),
    (12, "12 - December"),
]


class EligibilityForm(forms.ModelForm):
    fire = forms.ChoiceField(
        choices=VitalRecordsRequest.FIRE_CHOICES,
        label="Please confirm the fire you were impacted by",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["fire"]


class StatementForm(forms.ModelForm):
    relationship = forms.ChoiceField(
        choices=VitalRecordsRequest.RELATIONSHIP_CHOICES,
        label="Select your relationship",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    legal_attestation = forms.CharField(
        label="Type your full name to sign", max_length=386, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["relationship", "legal_attestation"]


class NameForm(forms.ModelForm):
    first_name = forms.CharField(
        label="First name at birth", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    middle_name = forms.CharField(
        label="Middle name at birth", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"}), required=False
    )
    last_name = forms.CharField(
        label="Last name at birth", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["first_name", "middle_name", "last_name"]


class CountyForm(forms.ModelForm):
    county_of_event = forms.ChoiceField(
        choices=VitalRecordsRequest.COUNTY_CHOICES,
        label="County of birth",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["county_of_event"]


class DateOfBirthForm(forms.ModelForm):
    birth_month = forms.ChoiceField(
        choices=MONTH_DISPLAY_CHOICES,
        label="Month",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    birth_day = forms.CharField(
        label="Day",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "bday-day",
                "required": "",
                "inputmode": "numeric",
                "pattern": "(3[01]|[12][0-9]|0?[1-9])",
                "maxlength": "2",
            },
        ),
    )
    birth_year = forms.CharField(
        label="Year",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "bday-year",
                "required": "",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "minlength": "4",
                "maxlength": "4",
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-populate form fields from model instance
        instance = kwargs.get("instance")
        if instance and instance.date_of_event:
            self.fields["birth_month"].initial = instance.date_of_event.month
            self.fields["birth_day"].initial = instance.date_of_event.day
            self.fields["birth_year"].initial = instance.date_of_event.year

    def clean(self):
        cleaned_data = super().clean()

        try:
            month = int(cleaned_data.get("birth_month"))
            day = int(cleaned_data.get("birth_day"))
            year = int(cleaned_data.get("birth_year"))

            cleaned_data["date_of_event"] = datetime.date(year, month, day)
        except (ValueError, TypeError):
            raise forms.ValidationError("Enter a valid date.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        date_of_event = self.cleaned_data.get("date_of_event")

        if date_of_event:
            instance.date_of_event = date_of_event

        if commit:
            instance.save()
        return instance

    class Meta:
        model = VitalRecordsRequest
        fields = []


class ParentsNamesForm(forms.ModelForm):
    person_1_first_name = forms.CharField(
        label="First name",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control", "aria-describedby": "parent_1_helptext"}),
    )
    person_1_last_name = forms.CharField(
        label="Last name at birth",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control", "aria-describedby": "parent_1_helptext"}),
    )
    person_2_first_name = forms.CharField(
        label="First name",
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "aria-describedby": "parent_2_helptext"}),
    )
    person_2_last_name = forms.CharField(
        label="Last name at birth",
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "aria-describedby": "parent_2_helptext"}),
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["person_1_first_name", "person_1_last_name", "person_2_first_name", "person_2_last_name"]


class OrderInfoForm(forms.ModelForm):
    number_of_records = forms.ChoiceField(
        choices=VitalRecordsRequest.NUMBER_CHOICES,
        label="Number of records",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    order_first_name = forms.CharField(
        label="First name", required=True, max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    order_last_name = forms.CharField(
        label="Last name", required=True, max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    address = forms.CharField(
        label="Street address", required=True, max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    address_2 = forms.CharField(
        label="Apartment, suite or unit",
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    city = forms.CharField(
        label="City", max_length=128, required=True, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    state = forms.ChoiceField(
        choices=VitalRecordsRequest.STATE_CHOICES,
        label="State",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    zip_code = forms.CharField(
        label="Zip code",
        max_length=10,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "numeric",
                "pattern": r"[\d]{5}(-[\d]{4})?",
            }
        ),
    )
    email_address = forms.CharField(
        label="Email address",
        required=True,
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "email"}),
    )
    phone_number = forms.CharField(
        label="Phone number",
        required=True,
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "numeric",
                "pattern": "^[0-9]+$",
                "type": "tel",
                "minlength": "10",
                "maxlength": "10",
            }
        ),
    )

    class Meta:
        model = VitalRecordsRequest
        fields = [
            "number_of_records",
            "order_first_name",
            "order_last_name",
            "address",
            "address_2",
            "city",
            "state",
            "zip_code",
            "email_address",
            "phone_number",
        ]


class SubmitForm(forms.ModelForm):

    class Meta:
        model = VitalRecordsRequest
        fields = []
