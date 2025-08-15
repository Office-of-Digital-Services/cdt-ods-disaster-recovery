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


class StepsContextMixin:
    STEPS = {
        "birth": {
            "Name": Routes.birth_request_name,
            "County of birth": Routes.birth_request_county,
            "Date of birth": Routes.birth_request_dob,
            "Parents' names": Routes.birth_request_parents,
            "Order information": Routes.request_order,
            "Preview & submit": Routes.request_submit,
        },
        "marriage": {
            "Name": Routes.marriage_request_name,
            "County of marriage": Routes.marriage_request_county,
            "Date of marriage": Routes.marriage_request_date,
            "Order information": Routes.request_order,
            "Preview & submit": Routes.request_submit,
        },
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        type_steps = self.STEPS[self.object.type]
        step_names = type_steps.keys()
        current_index = step_names.index(self.step_name)

        context["all_steps"] = step_names
        context["step_number"] = current_index + 1

        if current_index == 0:
            context["previous_route"] = Routes.request_statement
        else:
            previous_step_name = step_names[current_index - 1]
            context["previous_route"] = type_steps[previous_step_name]

        if current_index == len(step_names) - 1:
            next_route = Routes.request_submitted
        else:
            next_step_name = step_names[current_index + 1]
            next_route = type_steps[next_step_name]

        self.success_url = reverse(next_route, kwargs={"pk": self.object.pk})

        return context
