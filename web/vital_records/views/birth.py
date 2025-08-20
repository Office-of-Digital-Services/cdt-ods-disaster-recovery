from web.vital_records.forms.birth import NameForm
from web.vital_records.views import common
from web.vital_records.mixins import Steps


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


class CountyView(common.CountyView):
    step_name = Steps.county_of_birth
