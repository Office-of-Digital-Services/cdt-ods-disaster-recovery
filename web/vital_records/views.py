from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from web.vital_records import tasks
from web.vital_records.models import VitalRecordsRequest
from web.vital_records.session import Session
from web.vital_records.forms import (
    EligibilityForm,
    StatementForm,
    NameForm,
    CountyForm,
    DateOfBirthForm,
    ParentsNamesForm,
    OrderInfoForm,
    SubmitForm,
)


class IndexView(TemplateView):
    template_name = "vital_records/index.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        Session(request, reset=True)
        return super().get(request, *args, **kwargs)


class LoginView(RedirectView):
    permanent = False
    query_string = False
    pattern_name = "cdt:login"

    def dispatch(self, request, *args, **kwargs):
        Session(request, reset=True)
        return super().dispatch(request, *args, **kwargs)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context["name_fields"] = [
            form["first_name"],
            form["middle_name"],
            form["last_name"],
        ]

        return context

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
        return reverse("vital_records:request_parents", kwargs={"pk": self.object.pk})


class ParentsNamesView(UpdateView):
    model = VitalRecordsRequest
    form_class = ParentsNamesForm
    template_name = "vital_records/request/parents.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        # Move form state to next state
        self.object.complete_parents_names()
        self.object.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context["parent_1_fields"] = [
            form["parent_1_first_name"],
            form["parent_1_last_name"],
        ]
        context["parent_2_fields"] = [
            form["parent_2_first_name"],
            form["parent_2_last_name"],
        ]

        return context

    def get_success_url(self):
        return reverse("vital_records:request_order", kwargs={"pk": self.object.pk})


class OrderInfoView(UpdateView):
    model = VitalRecordsRequest
    form_class = OrderInfoForm
    template_name = "vital_records/request/order.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        # Move form state to next state
        self.object.complete_order_info()
        self.object.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context["name_fields"] = [
            form["order_first_name"],
            form["order_last_name"],
        ]

        return context

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
        return redirect(self.get_success_url())

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
        return reverse("vital_records:submitted", kwargs={"pk": self.object.pk})


class SubmittedView(DetailView):
    model = VitalRecordsRequest
    template_name = "vital_records/submitted.html"

    def get(self, request, *args, **kwargs):
        # Ensure self.object is initialized
        response = super().get(request, *args, **kwargs)
        # only enque a task if the request is in the correct state
        if self.object.status == "submitted":
            # Move to next state *before* putting task on the queue
            # Want to avoid race condition where the task is processed
            # off the queue before the state update is saved in DB!
            self.object.complete_enqueue()
            self.object.save()
            tasks.submit_request(self.object.pk)
            return response
        else:
            raise ValueError("Can't enqueue request: {} with status: {}")


class UnverifiedView(TemplateView):
    template_name = "vital_records/unverified.html"
