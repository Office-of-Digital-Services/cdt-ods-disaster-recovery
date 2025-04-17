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
