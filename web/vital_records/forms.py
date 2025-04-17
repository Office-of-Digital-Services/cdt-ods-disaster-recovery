from django import forms
from web.core.models import VitalRecordsRequest


class RequestEligibilityForm(forms.ModelForm):
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
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    legal_attestation = forms.CharField(label="Type your full name to sign", max_length=100, widget=forms.TextInput())

    class Meta:
        model = VitalRecordsRequest
        fields = ["relationship", "legal_attestation"]


class NameForm(forms.ModelForm):
    first_name = forms.CharField(label="First name at birth", max_length=100, widget=forms.TextInput())
    middle_name = forms.CharField(label="Middle name at birth", max_length=100, widget=forms.TextInput(), required=False)
    last_name = forms.CharField(label="Last name at birth", max_length=100, widget=forms.TextInput())

    class Meta:
        model = VitalRecordsRequest
        fields = ["first_name", "middle_name", "last_name"]
