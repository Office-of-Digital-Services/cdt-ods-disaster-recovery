from web.vital_records.forms.birth import CountyForm
from web.vital_records.forms.marriage import NameForm
from web.vital_records.mixins import Steps
from web.vital_records.views import common
from django.urls import reverse


class NameView(common.NameView):
    form_class = NameForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_layout"] = "couples_names_form"
        context["form_question"] = (
            "What are the names of the First Person and Second Person as they appear on the marriage record?"
        )
        context["form_hint"] = "Please write the information as it appears on the marriage certificate."
        context["font_hint_name"] = "name-hint"

        form = context["form"]
        context["person_1_fields"] = [
            form["person_1_first_name"],
            form["person_1_middle_name"],
            form["person_1_last_name"],
            form["person_1_birth_last_name"],
        ]
        context["person_1_label"] = "First person"
        context["person_1_labelid"] = "person_1_helptext"
        context["person_2_fields"] = [
            form["person_2_first_name"],
            form["person_2_middle_name"],
            form["person_2_last_name"],
            form["person_2_birth_last_name"],
        ]
        context["person_2_label"] = "Second person"
        context["person_2_labelid"] = "person_2_helptext"

        return context


class CountyView(common.CountyView):
    form_class = CountyForm
    step_name = Steps.county_of_marriage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_question"] = "Where did the marriage occur?"
        context["form_hint"] = (
            "We only have records for people who were married or had marriage"
            " licenses issued in California. If the marriage took place in a"
            " different state, please contact the Vital Records office in the"
            " state you were married to request a new record."
        )
        context["form_hint_name"] = "county-hint"

        form = context["form"]
        context["form_fields"] = [form["county_of_event"]]

        return context


class DateOfMarriageView(common.DateOfEventView):
    step_name = Steps.date_of_marriage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_layout"] = "date_form"
        context["font_hint_name"] = "marriage-date-hint"
        context["form_question"] = "What was the date of the marriage?"
        context["form_hint"] = "If you’re not sure, enter your approximate date of marriage."

        return context
