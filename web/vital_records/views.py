from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from web.core.views import EligibilityMixin as CoreEligibilityMixin
from web.vital_records.tasks.package import submit_request
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
from web.vital_records.mixins import ValidateRequestIdMixin
from web.vital_records.models import VitalRecordsRequest
from web.vital_records.session import Session


class EligibilityMixin(CoreEligibilityMixin):
    redirect_url = "vital_records:login"


class IndexView(TemplateView):
    template_name = "vital_records/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Replacement records"

        return context

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


class StartView(EligibilityMixin, CreateView):
    model = VitalRecordsRequest
    form_class = EligibilityForm
    template_name = "vital_records/request/start.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Replacement records"

        return context

    def form_valid(self, form):
        # set the object via form.save(), since we aren't using super().form_valid()
        self.object = form.save()
        # Move form state to next state
        next_route = self.object.complete_start()
        self.object.save()

        # store generated request id in session for verification in later steps
        Session(self.request, request_id=self.object.pk)

        return redirect(next_route, pk=self.object.pk)


class StatementView(EligibilityMixin, ValidateRequestIdMixin, UpdateView):
    model = VitalRecordsRequest
    form_class = StatementForm
    template_name = "vital_records/request/statement.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Replacement birth records"

        return context

    def form_valid(self, form):
        # Move form state to next state
        next_route = self.object.complete_statement()
        self.object.save()

        self.success_url = reverse(next_route, kwargs={"pk": self.object.pk})

        return super().form_valid(form)


class NameView(EligibilityMixin, ValidateRequestIdMixin, UpdateView):
    model = VitalRecordsRequest
    form_class = NameForm
    template_name = "vital_records/request/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Replacement birth records"
        context["total_steps"] = 6

        context["current_step"] = 1
        context["form_question"] = "What is the name on the birth certificate?"
        context["form_hint"] = "Please write the information as it appears on the birth certificate."
        context["font_hint_name"] = "name-hint"
        form = context["form"]
        context["form_columns"] = 2
        context["form_fields"] = [
            form["first_name"],
            form["middle_name"],
            form["last_name"],
        ]

        return context

    def form_valid(self, form):
        # Move form state to next state
        next_route = self.object.complete_name()
        self.object.save()

        self.success_url = reverse(next_route, kwargs={"pk": self.object.pk})

        return super().form_valid(form)


class CountyView(EligibilityMixin, ValidateRequestIdMixin, UpdateView):
    model = VitalRecordsRequest
    form_class = CountyForm
    template_name = "vital_records/request/form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Replacement birth records"
        context["total_steps"] = 6

        context["current_step"] = 2
        context["form_question"] = "What is the county of birth?"
        context["form_hint"] = (
            "We only have records for people born in California. If you were born in a different state, please contact the Vital Records office in the state you were born to request a new birth record."
        )
        context["font_hint_name"] = "county-hint"
        form = context["form"]
        context["form_columns"] = 2
        context["form_fields"] = [form["county_of_event"]]

        return context

    def form_valid(self, form):
        # Move form state to next state
        next_route = self.object.complete_county()
        self.object.save()

        self.success_url = reverse(next_route, kwargs={"pk": self.object.pk})

        return super().form_valid(form)


class DateOfBirthView(EligibilityMixin, ValidateRequestIdMixin, UpdateView):
    model = VitalRecordsRequest
    form_class = DateOfBirthForm
    template_name = "vital_records/request/dob.html"
    context_object_name = "vital_request"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Replacement birth records"
        context["total_steps"] = 6

        context["current_step"] = 3
        context["font_hint_name"] = "dob-hint"
        context["form_question"] = "What is the date of birth?"
        context["form_hint"] = "If you’re not sure, enter your approximate date of birth."

        return context

    def form_valid(self, form):
        # Move form state to next state
        next_route = self.object.complete_dob()
        self.object.save()

        self.success_url = reverse(next_route, kwargs={"pk": self.object.pk})

        return super().form_valid(form)


class ParentsNamesView(EligibilityMixin, ValidateRequestIdMixin, UpdateView):
    model = VitalRecordsRequest
    form_class = ParentsNamesForm
    template_name = "vital_records/request/parents.html"

    def form_valid(self, form):
        # Move form state to next state
        next_route = self.object.complete_parents_names()
        self.object.save()

        self.success_url = reverse(next_route, kwargs={"pk": self.object.pk})

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Replacement birth records"
        form = context["form"]
        context["person_1_fields"] = [
            form["person_1_first_name"],
            form["person_1_last_name"],
        ]
        context["person_2_fields"] = [
            form["person_2_first_name"],
            form["person_2_last_name"],
        ]

        return context


class OrderInfoView(EligibilityMixin, ValidateRequestIdMixin, UpdateView):
    model = VitalRecordsRequest
    form_class = OrderInfoForm
    template_name = "vital_records/request/order.html"

    def form_valid(self, form):
        # Move form state to next state
        next_route = self.object.complete_order_info()
        self.object.save()

        self.success_url = reverse(next_route, kwargs={"pk": self.object.pk})

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Replacement birth records"
        form = context["form"]
        context["name_fields"] = [
            form["order_first_name"],
            form["order_last_name"],
        ]

        return context


class SubmitView(EligibilityMixin, ValidateRequestIdMixin, UpdateView):
    model = VitalRecordsRequest
    form_class = SubmitForm
    template_name = "vital_records/request/confirm.html"
    context_object_name = "vital_records_request"

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.status != "submitted":
            next_route = self.object.complete_submit()
            self.success_url = reverse(next_route, kwargs={"pk": self.object.pk})
            self.object.save()
            return super().form_valid(form)
        else:
            form.add_error(None, "This request has already been submitted.")
            return self.form_invalid(form)

    def get_display_county(self, context):
        counties = VitalRecordsRequest.COUNTY_CHOICES
        county_of_birth_id = context["vital_records_request"].county_of_event

        # Make sure the ID is not blank ("") and ID is in the county options list
        if county_of_birth_id != "" and county_of_birth_id in dict(counties):
            return dict(counties)[county_of_birth_id]
        else:
            return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Replacement birth records"
        context["county_display"] = self.get_display_county(context)
        return context


class SubmittedView(EligibilityMixin, ValidateRequestIdMixin, DetailView):
    model = VitalRecordsRequest
    template_name = "vital_records/submitted.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Replacement birth records"
        return context

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
            submit_request(self.object.pk)
            return response
        else:
            raise ValueError("Can't enqueue request: {} with status: {}")


class UnverifiedView(TemplateView):
    template_name = "vital_records/unverified.html"
