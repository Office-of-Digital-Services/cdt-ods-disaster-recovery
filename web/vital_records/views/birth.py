from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from web.vital_records.forms.birth import CountyForm, NameForm
from web.vital_records.views import common
from web.vital_records.mixins import Steps


@method_decorator(never_cache, name="dispatch")
class NameView(common.NameView):
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


@method_decorator(never_cache, name="dispatch")
class CountyView(common.CountyView):
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


@method_decorator(never_cache, name="dispatch")
class DateOfBirthView(common.DateOfEventView):
    step_name = Steps.date_of_birth

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_layout"] = "date_form"
        context["font_hint_name"] = "dob-hint"
        context["form_question"] = "What is the date of birth?"
        context["form_hint"] = "If you’re not sure, enter your approximate date of birth."

        return context
