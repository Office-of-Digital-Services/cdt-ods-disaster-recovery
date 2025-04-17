from typing import Any

from django.http import HttpRequest
from django.shortcuts import redirect
from django.views import View
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView, DetailView

from web.core.models import VitalRecordsRequest
from web.vital_records.session import Session
from web.vital_records.forms import RequestEligibilityForm, StatementForm, NameForm


class IndexView(TemplateView):
    template_name = "vital_records/index.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        Session(request, reset=True)
        return super().get(request, *args, **kwargs)


class LoginView(View):
    def get(self, request: HttpRequest):
        Session(request, reset=True)
        return redirect("cdt:login")


class EligibilityView(CreateView):
    model = VitalRecordsRequest
    form_class = RequestEligibilityForm
    template_name = "vital_records/request/eligibility.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        # Move form state to next state
        self.object.complete_eligibility()
        self.object.save()

        return response

    def get_success_url(self):
        return reverse("vital_records:request_statement", kwargs={"pk": self.object.pk})


class StatementView(UpdateView):
    model = VitalRecordsRequest
    form_class = StatementForm
    template_name = "vital_records/request/statement.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        # Move form state to next state
        self.object.complete_statement()
        self.object.save()

        return response

    def get_success_url(self):
        return reverse("vital_records:request_name", kwargs={"pk": self.object.pk})


class NameView(UpdateView):
    model = VitalRecordsRequest
    form_class = NameForm
    template_name = "vital_records/request/name.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        # Move form state to next state
        self.object.complete_name()
        self.object.save()

        return response

    def get_success_url(self):
        return reverse("vital_records:request_detail", kwargs={"pk": self.object.pk})


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
