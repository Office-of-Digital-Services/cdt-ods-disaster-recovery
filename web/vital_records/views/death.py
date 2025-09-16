from django.views.generic.edit import UpdateView

from web.vital_records.forms.death import NameForm
from web.vital_records.mixins import ValidateTypeMixin
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


class CountyView(common.CountyView):
    pass


class DateOfDeathView(common.DateOfEventView):
    pass


class DateOfBirthView(common.DateOfEventView):
    pass


class ParentView(UpdateView):
    pass


class SpouseView(UpdateView):
    pass
