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


class TypeForm(forms.ModelForm):
    type = forms.ChoiceField(
        choices=VitalRecordsRequest.TYPE_CHOICES,
        label="Select record type",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["type"]


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
