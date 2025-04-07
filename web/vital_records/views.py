from typing import Any

from django.http import HttpRequest
from django.views.generic import TemplateView

from web.vital_records.session import Session


class IndexView(TemplateView):
    template_name = "vital_records/index.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        Session(request, reset=True)
        return super().get(request, *args, **kwargs)


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
