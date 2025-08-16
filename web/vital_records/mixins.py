from django.http import HttpResponseForbidden
from django.urls import reverse

from web.vital_records.routes import Routes
from web.vital_records.session import Session


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


class StepsContextMixin:
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        type_steps = self.STEPS[self.object.type]
        step_names = list(type_steps.keys())
        current_index = step_names.index(self.step_name)

        context["all_steps"] = step_names
        context["step_number"] = current_index + 1

        if current_index == 0:
            previous_route_name = Routes.request_statement
        else:
            previous_step_name = step_names[current_index - 1]
            previous_route_name = type_steps[previous_step_name]

        context["previous_route"] = Routes.app_route(previous_route_name)

        if current_index == len(step_names) - 1:
            next_route_name = Routes.request_submitted
        else:
            next_step_name = step_names[current_index + 1]
            next_route_name = type_steps[next_step_name]

        next_route = Routes.app_route(next_route_name)
        self.success_url = reverse(next_route, kwargs={"pk": self.object.pk})

        return context
