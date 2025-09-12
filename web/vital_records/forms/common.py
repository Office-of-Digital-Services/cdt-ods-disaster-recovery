import datetime
from django import forms

from web.vital_records.mixins import DisableFieldsMixin
from web.vital_records.models import VitalRecordsRequest

COUNTY_CHOICES = [
    ("", "Select county"),
    ("Alameda", "Alameda"),
    ("Alpine", "Alpine"),
    ("Amador", "Amador"),
    ("Butte", "Butte"),
    ("Calaveras", "Calaveras"),
    ("Colusa", "Colusa"),
    ("Contra Costa", "Contra Costa"),
    ("Del Norte", "Del Norte"),
    ("El Dorado", "El Dorado"),
    ("Fresno", "Fresno"),
    ("Glenn", "Glenn"),
    ("Humboldt", "Humboldt"),
    ("Imperial", "Imperial"),
    ("Inyo", "Inyo"),
    ("Kern", "Kern"),
    ("Kings", "Kings"),
    ("Lake", "Lake"),
    ("Lassen", "Lassen"),
    ("Los Angeles", "Los Angeles"),
    ("Madera", "Madera"),
    ("Marin", "Marin"),
    ("Mariposa", "Mariposa"),
    ("Mendocino", "Mendocino"),
    ("Merced", "Merced"),
    ("Modoc", "Modoc"),
    ("Mono", "Mono"),
    ("Monterey", "Monterey"),
    ("Napa", "Napa"),
    ("Nevada", "Nevada"),
    ("Orange", "Orange"),
    ("Placer", "Placer"),
    ("Plumas", "Plumas"),
    ("Riverside", "Riverside"),
    ("Sacramento", "Sacramento"),
    ("San Benito", "San Benito"),
    ("San Bernardino", "San Bernardino"),
    ("San Diego", "San Diego"),
    ("San Francisco", "San Francisco"),
    ("San Joaquin", "San Joaquin"),
    ("San Luis Obispo", "San Luis Obispo"),
    ("San Mateo", "San Mateo"),
    ("Santa Barbara", "Santa Barbara"),
    ("Santa Clara", "Santa Clara"),
    ("Santa Cruz", "Santa Cruz"),
    ("Shasta", "Shasta"),
    ("Sierra", "Sierra"),
    ("Siskiyou", "Siskiyou"),
    ("Solano", "Solano"),
    ("Sonoma", "Sonoma"),
    ("Stanislaus", "Stanislaus"),
    ("Sutter", "Sutter"),
    ("Tehama", "Tehama"),
    ("Trinity", "Trinity"),
    ("Tulare", "Tulare"),
    ("Tuolumne", "Tuolumne"),
    ("Ventura", "Ventura"),
    ("Yolo", "Yolo"),
    ("Yuba", "Yuba"),
]

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

STATE_CHOICES = [
    ("", "Select state"),
    ("AK", "Alaska"),
    ("AL", "Alabama"),
    ("AR", "Arkansas"),
    ("AS", "American Samoa"),
    ("AZ", "Arizona"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DC", "District of Columbia"),
    ("DE", "Delaware"),
    ("FL", "Florida"),
    ("FM", "Federated States of Micronesia"),
    ("GA", "Georgia"),
    ("GU", "Guam"),
    ("HI", "Hawaii"),
    ("IA", "Iowa"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("MA", "Massachusetts"),
    ("MD", "Maryland"),
    ("ME", "Maine"),
    ("MH", "Marshall Islands"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MO", "Missouri"),
    ("MP", "Northern Mariana Islands"),
    ("MS", "Mississippi"),
    ("MT", "Montana"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("NE", "Nebraska"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NV", "Nevada"),
    ("NY", "New York"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("PR", "Puerto Rico"),
    ("PW", "Palau"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VA", "Virginia"),
    ("VI", "Virgin Islands"),
    ("VT", "Vermont"),
    ("WA", "Washington"),
    ("WI", "Wisconsin"),
    ("WV", "West Virginia"),
    ("WY", "Wyoming"),
]

TYPE_CHOICES = [("", "Select type"), ("birth", "Birth record"), ("marriage", "Marriage record"), ("death", "Death record")]


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
        choices=STATE_CHOICES,
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
