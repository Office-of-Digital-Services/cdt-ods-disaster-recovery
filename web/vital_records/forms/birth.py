from django import forms

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
