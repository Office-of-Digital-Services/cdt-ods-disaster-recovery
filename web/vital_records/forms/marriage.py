from django import forms

from web.vital_records.mixins import DisableFieldsMixin
from web.vital_records.models import VitalRecordsRequest


class NameForm(DisableFieldsMixin, forms.ModelForm):
    person_1_first_name = forms.CharField(
        label="First name", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    person_1_middle_name = forms.CharField(
        label="Middle name", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"}), required=False
    )
    person_1_last_name = forms.CharField(
        label="Current last name", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    person_1_birth_last_name = forms.CharField(
        label="Last name at birth", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    person_2_first_name = forms.CharField(
        label="First name", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    person_2_middle_name = forms.CharField(
        label="Middle name", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"}), required=False
    )
    person_2_last_name = forms.CharField(
        label="Current last name", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    person_2_birth_last_name = forms.CharField(
        label="Last name at birth", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = VitalRecordsRequest
        fields = [
            "person_1_first_name",
            "person_1_middle_name",
            "person_1_last_name",
            "person_1_birth_last_name",
            "person_2_first_name",
            "person_2_middle_name",
            "person_2_last_name",
            "person_2_birth_last_name",
        ]


class CountyForm(DisableFieldsMixin, forms.ModelForm):
    county_of_event = forms.ChoiceField(
        choices=VitalRecordsRequest.COUNTY_CHOICES,
        label="County marriage occurred/license issued",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["county_of_event"]
