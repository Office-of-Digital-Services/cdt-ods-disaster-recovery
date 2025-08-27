from django.http import HttpResponseForbidden
from django.urls import reverse
from django.views.generic.base import ContextMixin

from web.vital_records.routes import Routes
from web.vital_records.session import Session


class DisableFieldsMixin:
    def __init__(self, *args, **kwargs):
        super(DisableFieldsMixin, self).__init__(*args, **kwargs)
        if hasattr(self, "instance") and self.instance is not None and self.instance.already_submitted:
            for field_name, field in self.fields.items():
                field.disabled = True


class ValidateRequestIdMixin:
    def dispatch(self, request, *args, **kwargs):
        session = Session(request)
        request_id = self.kwargs.get("pk")

        if session.request_id == request_id:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()


class Steps:
    name = "Name"
    county_of_birth = "County of birth"
    date_of_birth = "Date of birth"
    parents_names = "Parents' names"
    county_of_marriage = "County of marriage"
    date_of_marriage = "Date of marriage"
    order_information = "Order information"
    preview_and_submit = "Preview & submit"


class StepsMixin(ContextMixin):
    STEPS = {
        "birth": {
            Steps.name: Routes.birth_request_name,
            Steps.county_of_birth: Routes.birth_request_county,
            Steps.date_of_birth: Routes.birth_request_dob,
            Steps.parents_names: Routes.birth_request_parents,
            Steps.order_information: Routes.request_order,
            Steps.preview_and_submit: Routes.request_submit,
        },
        "marriage": {
            Steps.name: Routes.marriage_request_name,
            Steps.county_of_marriage: Routes.marriage_request_county,
            Steps.date_of_marriage: Routes.marriage_request_date,
            Steps.order_information: Routes.request_order,
            Steps.preview_and_submit: Routes.request_submit,
        },
    }

    @staticmethod
    def get_type_steps(type):
        return StepsMixin.STEPS[type]

    @staticmethod
    def get_step_names(type_steps):
        return list(type_steps.keys())

    def get_current_index(self, step_names):
        return step_names.index(self.step_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        type_steps = self.get_type_steps(self.object.type)
        step_names = self.get_step_names(type_steps)
        current_index = self.get_current_index(step_names)

        context["page_title"] = f"Replacement {self.object.type} record"
        context["all_steps"] = step_names
        context["step_number"] = current_index + 1

        if current_index == 0:
            previous_route_name = Routes.request_statement
        else:
            previous_step_name = step_names[current_index - 1]
            previous_route_name = type_steps[previous_step_name]

        previous_route = Routes.app_route(previous_route_name)
        context["previous_url"] = reverse(previous_route, kwargs={"pk": self.object.pk})

        return context

    def get_success_url(self):
        type_steps = self.get_type_steps(self.object.type)
        step_names = self.get_step_names(type_steps)
        current_index = self.get_current_index(step_names)

        if current_index == len(step_names) - 1:
            next_route_name = Routes.request_submitted
        else:
            next_step_name = step_names[current_index + 1]
            next_route_name = type_steps[next_step_name]

        next_route = Routes.app_route(next_route_name)

        return reverse(next_route, kwargs={"pk": self.object.pk})
