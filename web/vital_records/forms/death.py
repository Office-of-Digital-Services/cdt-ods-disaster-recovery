from django import forms

from web.vital_records.mixins import DisableFieldsMixin
from web.vital_records.models import VitalRecordsRequest


class NameForm(DisableFieldsMixin, forms.ModelForm):
    first_name = forms.CharField(label="First name", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"}))
    middle_name = forms.CharField(
        label="Middle name", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"}), required=False
    )
    last_name = forms.CharField(
        label="Last name at birth", max_length=128, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = VitalRecordsRequest
        fields = ["first_name", "middle_name", "last_name"]
