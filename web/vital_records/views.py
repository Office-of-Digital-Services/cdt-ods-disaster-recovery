from typing import Any

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from web.vital_records.models import VitalRecordsRequest
from web.vital_records.session import Session
from web.vital_records.forms import EligibilityForm, StatementForm, NameForm, CountyForm, DateOfBirthForm, SubmitForm


class IndexView(TemplateView):
    template_name = "vital_records/index.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        Session(request, reset=True)
        return super().get(request, *args, **kwargs)


class LoginView(View):
    def get(self, request: HttpRequest):
        Session(request, reset=True)
        return redirect("cdt:login")


class RequestView(TemplateView):
    template_name = "vital_records/request.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        session = Session(self.request)
        context = super().get_context_data(**kwargs)
        context["email"] = session.verified_email
        return context


class EligibilityView(CreateView):
    model = VitalRecordsRequest
    form_class = EligibilityForm
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
        return reverse("vital_records:request_county", kwargs={"pk": self.object.pk})


class CountyView(UpdateView):
    model = VitalRecordsRequest
    form_class = CountyForm
    template_name = "vital_records/request/county.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        # Move form state to next state
        self.object.complete_county()
        self.object.save()

        return response

    def get_success_url(self):
        return reverse("vital_records:request_dob", kwargs={"pk": self.object.pk})


class DateOfBirthView(UpdateView):
    model = VitalRecordsRequest
    form_class = DateOfBirthForm
    template_name = "vital_records/request/dob.html"
    context_object_name = "vital_request"

    def form_valid(self, form):
        response = super().form_valid(form)

        # Move form state to next state
        self.object.complete_dob()
        self.object.save()

        return response

    def get_success_url(self):
        return reverse("vital_records:request_submit", kwargs={"pk": self.object.pk})


class SubmitView(UpdateView):
    model = VitalRecordsRequest
    form_class = SubmitForm
    template_name = "vital_records/request/confirm.html"
    context_object_name = "vital_records_request"

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.status != "submitted":
            self.object.complete_submit()
        else:
            form.add_error(None, "This request has already been submitted.")
            return self.form_invalid(form)

        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_display_county(self, context):
        counties = VitalRecordsRequest.COUNTY_CHOICES
        county_of_birth_id = context["vital_records_request"].county_of_birth

        # Make sure the ID is not blank ("") and ID is in the county options list
        if county_of_birth_id != "" and county_of_birth_id in dict(counties):
            return dict(counties)[county_of_birth_id]
        else:
            return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["county_display"] = self.get_display_county(context)
        return context

    def get_success_url(self):
        return reverse("vital_records:submitted")


class SubmittedView(TemplateView):
    template_name = "vital_records/submitted.html"


class UnverifiedView(TemplateView):
    template_name = "vital_records/unverified.html"
