from django.views.generic.edit import UpdateView

from web.vital_records.forms.death import NameForm, CountyForm
from web.vital_records.mixins import Steps, ValidateTypeMixin
from web.vital_records.views import common


class NameView(ValidateTypeMixin, common.NameView):
    form_class = NameForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_question"] = "What is the name on the death record?"
        context["form_hint"] = "Please write the information as it appears on the death record."
        context["form_hint_name"] = "name-hint"
        form = context["form"]

        context["form_fields"] = [
            form["first_name"],
            form["middle_name"],
            form["last_name"],
        ]

        return context


class CountyView(ValidateTypeMixin, common.CountyView):
    form_class = CountyForm
    step_name = Steps.county_of_death

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_question"] = "What was the county of death?"
        context["form_hint"] = (
            "We can only issue death records for deaths that occurred in California. If the death took place in a "
            "different state, please contact the Vital Records office in the state the death occurred in to request "
            "a new record."
        )
        context["form_hint_name"] = "county-hint"
        form = context["form"]

        context["form_fields"] = [form["county_of_event"]]

        return context


class DateOfDeathView(ValidateTypeMixin, common.DateOfEventView):
    step_name = Steps.date_of_death

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_layout"] = "date_form"
        context["form_hint_name"] = "death-date-hint"
        context["form_question"] = "What was the date of death?"
        context["form_hint"] = "If you’re not sure, enter their approximate date of death."

        return context


class DateOfBirthView(ValidateTypeMixin, common.DateOfBirthView):
    step_name = Steps.date_of_birth

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_question"] = "What was the deceased person’s date of birth?"
        context["form_layout"] = "date_form"
        context["form_hint"] = "If you’re not sure, enter their approximate date of birth."
        context["form_hint_name"] = "dob-hint"

        return context


class ParentView(UpdateView):
    pass


class SpouseView(UpdateView):
    pass
