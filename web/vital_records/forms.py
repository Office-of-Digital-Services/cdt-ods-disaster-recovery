from django import forms
from web.core.models import VitalRecordsRequest


class RequestEligibilityForm(forms.ModelForm):
    fire = forms.ChoiceField(choices=VitalRecordsRequest.FIRE_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))

    class Meta:
        model = VitalRecordsRequest
        fields = ["fire"]
