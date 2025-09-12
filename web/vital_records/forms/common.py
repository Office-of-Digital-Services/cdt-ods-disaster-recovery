import datetime
from django import forms

from web.vital_records.mixins import DisableFieldsMixin
from web.vital_records.models import VitalRecordsRequest

FIRE_CHOICES = [
    ("", "Select fire"),
    ("eaton", "Eaton fire"),
    ("hurst", "Hurst fire"),
    ("lidia", "Lidia fire"),
    ("palisades", "Palisades fire"),
    ("woodley", "Woodley fire"),
]

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

RELATIONSHIP_CHOICES = [
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
]

TYPE_CHOICES = [("", "Select type"), ("birth", "Birth record"), ("marriage", "Marriage record")]


class EligibilityForm(forms.ModelForm):
    fire = forms.ChoiceField(
        choices=FIRE_CHOICES,
        label="Please confirm the fire you were impacted by",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["fire"]


class TypeForm(DisableFieldsMixin, forms.ModelForm):
    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label="Select record type",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["type"]


class StatementForm(DisableFieldsMixin, forms.ModelForm):
    relationship = forms.ChoiceField(
        choices=RELATIONSHIP_CHOICES,
        label="Select your relationship",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    legal_attestation = forms.CharField(
        label="Type your full name to sign", max_length=386, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["relationship", "legal_attestation"]


class DateOfEventForm(DisableFieldsMixin, forms.ModelForm):
    month = forms.ChoiceField(
        choices=MONTH_DISPLAY_CHOICES,
        label="Month",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    day = forms.CharField(
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
    year = forms.CharField(
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
            self.fields["month"].initial = instance.date_of_event.month
            self.fields["day"].initial = instance.date_of_event.day
            self.fields["year"].initial = instance.date_of_event.year

    def clean(self):
        cleaned_data = super().clean()

        try:
            month = int(cleaned_data.get("month"))
            day = int(cleaned_data.get("day"))
            year = int(cleaned_data.get("year"))

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


class OrderInfoForm(DisableFieldsMixin, forms.ModelForm):
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
