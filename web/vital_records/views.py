from typing import Any

from django.http import HttpRequest
from django.shortcuts import redirect
from django.views import View
from django.urls import reverse
from django.views.generic.edit import FormView
from django.views.generic import TemplateView, DetailView

from web.core.models import VitalRecordsRequest
from web.vital_records.session import Session
from web.vital_records.forms import RequestEligibilityForm


class IndexView(TemplateView):
    template_name = "vital_records/index.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        Session(request, reset=True)
        return super().get(request, *args, **kwargs)


class LoginView(View):
    def get(self, request: HttpRequest):
        Session(request, reset=True)
        return redirect("cdt:login")


class EligibilityView(FormView):
    template_name = "vital_records/request/eligibility.html"
    form_class = RequestEligibilityForm

    def form_valid(self, form):
        # Save vital record request form data
        self.object = form.save()

        # Move form state to next state
        self.object.complete_eligibility()

        self.object.save()
        return redirect(reverse("vital_records:request_detail", kwargs={"pk": self.object.pk}))


class VitalRecordsRequestDetailView(DetailView):
    model = VitalRecordsRequest
    template_name = "vital_records/request/confirmation.html"
    context_object_name = "vital_records_request"


class RequestView(TemplateView):
    template_name = "vital_records/request.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        session = Session(self.request)
        context = super().get_context_data(**kwargs)
        context["email"] = session.verified_email
        return context


class SubmittedView(TemplateView):
    template_name = "vital_records/submitted.html"


class UnverifiedView(TemplateView):
    template_name = "vital_records/unverified.html"
