from web.vital_records.forms.marriage import NameForm
from web.vital_records.views import common


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
            form["person_1_birth_last_name"]
        ]
        context["person_1_label"] = "First person"
        context["person_1_labelid"] = "person_1_helptext"
        context["person_2_fields"] = [
            form["person_2_first_name"],
            form["person_2_middle_name"],
            form["person_2_last_name"],
            form["person_2_birth_last_name"]
        ]
        context["person_2_label"] = "Second person"
        context["person_2_labelid"] = "person_2_helptext"

        return context
