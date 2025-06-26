import datetime
from django import forms

from web.vital_records.models import VitalRecordsRequest


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
        label="Type your full name to sign", max_length=256, widget=forms.TextInput(attrs={"class": "form-control"})
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
    county_of_birth = forms.ChoiceField(
        choices=VitalRecordsRequest.COUNTY_CHOICES,
        label="County of birth",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["county_of_birth"]


class DateOfBirthForm(forms.ModelForm):
    birth_month = forms.CharField(
        label="Month",
        help_text="MM",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "bday-month",
                "required": "",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "maxlength": "2",
                "aria-describedby": "id_birth_month_helptext",
            },
        ),
    )
    birth_day = forms.CharField(
        label="Day",
        help_text="DD",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "bday-day",
                "required": "",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "maxlength": "2",
                "aria-describedby": "id_birth_day_helptext",
            },
        ),
    )
    birth_year = forms.CharField(
        label="Year",
        help_text="YYYY",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "bday-year",
                "required": "",
                "inputmode": "numeric",
                "pattern": "[0-9]*",
                "minlength": "4",
                "maxlength": "4",
                "aria-describedby": "id_birth_year_helptext",
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-populate form fields from model instance
        instance = kwargs.get("instance")
        if instance and instance.date_of_birth:
            self.fields["birth_month"].initial = instance.date_of_birth.month
            self.fields["birth_day"].initial = instance.date_of_birth.day
            self.fields["birth_year"].initial = instance.date_of_birth.year

    def clean(self):
        cleaned_data = super().clean()

        try:
            month = int(cleaned_data.get("birth_month"))
            day = int(cleaned_data.get("birth_day"))
            year = int(cleaned_data.get("birth_year"))

            cleaned_data["date_of_birth"] = datetime.date(year, month, day)
        except (ValueError, TypeError):
            raise forms.ValidationError("Enter a valid date.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        date_of_birth = self.cleaned_data.get("date_of_birth")

        if date_of_birth:
            instance.date_of_birth = date_of_birth

        if commit:
            instance.save()
        return instance

    class Meta:
        model = VitalRecordsRequest
        fields = []


class ParentsNamesForm(forms.ModelForm):
    parent_1_first_name = forms.CharField(
        label="First name",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control", "aria-describedby": "parent_1_helptext"}),
    )
    parent_1_last_name = forms.CharField(
        label="Last name at birth",
        max_length=128,
        widget=forms.TextInput(attrs={"class": "form-control", "aria-describedby": "parent_1_helptext"}),
    )
    parent_2_first_name = forms.CharField(
        label="First name",
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "aria-describedby": "parent_2_helptext"}),
    )
    parent_2_last_name = forms.CharField(
        label="Last name at birth",
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "aria-describedby": "parent_2_helptext"}),
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["parent_1_first_name", "parent_1_last_name", "parent_2_first_name", "parent_2_last_name"]


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
    address = forms.CharField(label="Street address", max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    city = forms.CharField(label="City", max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    state = forms.ChoiceField(
        choices=VitalRecordsRequest.STATE_CHOICES,
        label="State",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    zip_code = forms.CharField(
        label="Zip code",
        max_length=5,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "numeric",
                "minlength": "5",
                "maxlength": "5",
            }
        ),
    )
    email_address = forms.CharField(
        label="Email address",
        required=True,
        max_length=50,
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
