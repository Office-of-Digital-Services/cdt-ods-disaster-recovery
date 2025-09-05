from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.edit import UpdateView

from web.core.views import EligibilityMixin
from web.vital_records.forms.birth import CountyForm, NameForm, ParentsNamesForm
from web.vital_records.models import VitalRecordsRequest
from web.vital_records.views import common
from web.vital_records.mixins import Steps, StepsMixin, ValidateRequestIdMixin, ValidateTypeMixin


class NameView(ValidateTypeMixin, common.NameView):
    form_class = NameForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_question"] = "What is the name on the birth certificate?"
        context["form_hint"] = "Please write the information as it appears on the birth certificate."
        context["font_hint_name"] = "name-hint"
        form = context["form"]

        context["form_fields"] = [
            form["first_name"],
            form["middle_name"],
            form["last_name"],
        ]

        return context


class CountyView(ValidateTypeMixin, common.CountyView):
    form_class = CountyForm
    step_name = Steps.county_of_birth

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_question"] = "What is the county of birth?"
        context["form_hint"] = (
            "We only have records for people born in California. If you were born in a different state, please contact the "
            "Vital Records office in the state you were born to request a new birth record."
        )
        context["font_hint_name"] = "county-hint"
        form = context["form"]

        context["form_fields"] = [form["county_of_event"]]

        return context


class DateOfBirthView(ValidateTypeMixin, common.DateOfEventView):
    step_name = Steps.date_of_birth

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_layout"] = "date_form"
        context["font_hint_name"] = "dob-hint"
        context["form_question"] = "What is the date of birth?"
        context["form_hint"] = "If you’re not sure, enter your approximate date of birth."

        return context


@method_decorator(never_cache, name="dispatch")
class ParentsNamesView(ValidateTypeMixin, StepsMixin, EligibilityMixin, ValidateRequestIdMixin, UpdateView):
    model = VitalRecordsRequest
    form_class = ParentsNamesForm
    template_name = "vital_records/request/form.html"
    step_name = Steps.parents_names

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_layout"] = "couples_names_form"
        context["font_hint_name"] = "parents-hint"
        context["form_question"] = "What were the names of the registrant’s parents at the time of the registrant’s birth?"
        context["form_hint"] = "Please write the information as it appears on the birth certificate."
        form = context["form"]
        context["person_1_fields"] = [
            form["person_1_first_name"],
            form["person_1_last_name"],
        ]
        context["person_1_label"] = "Parent 1"
        context["person_1_labelid"] = "parent_1_helptext"
        context["person_2_fields"] = [
            form["person_2_first_name"],
            form["person_2_last_name"],
        ]
        context["person_2_label"] = "Parent 2"
        context["person_2_labelid"] = "parent_2_helptext"

        return context
