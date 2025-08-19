import datetime

from django import forms

from web.vital_records.forms.common import MONTH_DISPLAY_CHOICES
from web.vital_records.models import VitalRecordsRequest


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
